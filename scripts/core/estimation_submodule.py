from datetime import datetime
from filterpy.kalman import KalmanFilter
from filterpy.kalman import ExtendedKalmanFilter
import numpy as np
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag

class LinearKinematic:

    SIMULATED_DT = None
    
    def __init__(self, measurement_noise, process_noise, initial_gain):
        self.position = (0,0)
        self.velocity = (0,0)
        self.timestamp = datetime.now()
        self.error = None
        self.delta_t = 0
        self.measurement_noise = measurement_noise
        self.process_noise = process_noise
        self.initial_gain = initial_gain
        self.kf = self.init_kalman_filter()


    def init_kalman_filter(self):
        kf = KalmanFilter(dim_x=4, dim_z=2)
        kf.alpha = 1
        kf.x = None
        kf.F = np.array([[1., self.delta_t, 0., 0.],
                         [0., 1., 0., 0.],
                         [0., 0., 1., self.delta_t],
                         [0., 0., 0., 1.]])
        kf.H = np.array([[1., 0., 0., 0.],
                         [0., 0., 1., 0.]])
        kf.P *= np.diag(self.initial_gain)
        kf.R = np.array([[self.measurement_noise, 0],
                         [0, self.measurement_noise]
                         ])
        
        q = Q_discrete_white_noise(dim=2, dt=self.delta_t, var=self.process_noise)
        LinearKinematic.Q = block_diag(q, q)
        return kf

   
    def apply_kalman_filter(self, x, y):
        if self.kf.x is None:
            self.kf.x = np.array([1., 0., 1., 0.])
        self.kf.predict()
        self.kf.update([[x, y]])
        x = self.kf.x[0]
        y = self.kf.x[2]
        vx = self.kf.x[1]
        vy = self.kf.x[3]
        return x, y, vx, vy
       
    def update(self, estimated_x, estimated_y):
        timestamp_now = datetime.now()
        if LinearKinematic.SIMULATED_DT is None:
            self.delta_t = (timestamp_now - self.timestamp).microseconds / 1e+6
        else:
            self.delta_t = LinearKinematic.SIMULATED_DT
        q = Q_discrete_white_noise(dim=2, dt=self.delta_t, var=self.process_noise)
        self.kf.Q = block_diag(q, q)
        self.kf.F[0][1] = self.delta_t
        self.kf.F[2][3] = self.delta_t
        x, y, vx, vy = self.apply_kalman_filter(estimated_x, estimated_y)
        self.position = (x, y)
        self.velocity = (vx * 1.94384, vy * 1.94384)
        self.timestamp = timestamp_now
        
class NonLinearKinematic:

    def __init__(self, measurement_noise_r, measurement_noise_theta, process_noise, initial_gain):
        self.position = (0, 0)
        self.velocity = (0, 0)
        self.timestamp = datetime.now()
        self.delta_t = 0
        self.measurement_noise_r = measurement_noise_r
        self.measurement_noise_theta = measurement_noise_theta
        self.process_noise = process_noise
        self.initial_gain = initial_gain
        self.ekf = self.init_ekf()

    def fx(self, x, dt):
        return np.array([
            x[0] + x[1] * dt,
            x[1],
            x[2] + x[3] * dt,
            x[3]
        ])
    
    # def fx(self, x, dt):
    #     px, py, v, theta = x
    #     px_new = px + v * np.cos(theta) * dt
    #     py_new = py + v * np.sin(theta) * dt
    #     theta_new = theta  # ou theta + omega * dt, se tiver rotação
    #     return np.array([px_new, py_new, v, theta_new])

    def hx(self, x):
        px, vx, py, vy = x
        r = np.sqrt(px**2 + py**2)
        theta = np.arctan2(py, px)  
        return np.array([r, theta])

    def jacobian_F(self, x, dt):
        return np.array([
            [1, dt, 0,  0],
            [0, 1,  0,  0],
            [0, 0,  1, dt],
            [0, 0,  0, 1]
        ])

    def jacobian_H(self, x):
        px, vx, py, vy = x
        denom = px**2 + py**2
        if denom < 1e-4:
            denom = 1e-4

        sqrt_denom = np.sqrt(denom)

        return np.array([
            [px / sqrt_denom, 0, py / sqrt_denom, 0],
            [-py / denom,     0, px / denom,      0]
        ])
    
   
    def init_ekf(self):
        ekf = ExtendedKalmanFilter(dim_x=4, dim_z=2)
        ekf.x = None
        ekf.P = np.diag(self.initial_gain)
        ekf.R = np.array([
            [self.measurement_noise_r, 0],
            [0, self.measurement_noise_theta]
        ])
        ekf.Q = block_diag(
            Q_discrete_white_noise(dim=2, dt=1.0, var=self.process_noise),
            Q_discrete_white_noise(dim=2, dt=1.0, var=self.process_noise)
        )
        return ekf

    def apply_ekf(self, r, theta):
        if self.ekf.x is None:
            x0 = r * np.cos(theta)
            y0 = r * np.sin(theta)
            self.ekf.x = np.array([x0, 0., y0, 0.])

        self.ekf.F = self.jacobian_F(self.ekf.x, self.delta_t)

        self.ekf.predict()

        self.ekf.update(
            z=np.array([r,theta]),
            HJacobian=self.jacobian_H,
            Hx=self.hx,
            residual=self.residual
        )

        x = self.ekf.x[0]
        y = self.ekf.x[2]
        vx = self.ekf.x[1]
        vy = self.ekf.x[3]
        return x, y, vx, vy

    def update(self, measured_r, measured_theta):
        timestamp_now = datetime.now()
        self.delta_t = (timestamp_now - self.timestamp).total_seconds()
        q = Q_discrete_white_noise(dim=2, dt=self.delta_t, var=self.process_noise)
        self.ekf.Q = block_diag(q, q)

        x, y, vx, vy = self.apply_ekf(measured_r, measured_theta)

        self.position = (x, y)
        self.velocity = (vx * 1.94384, vy * 1.94384)
        self.timestamp = timestamp_now

    @staticmethod
    def residual(a, b):
        y = a - b
        y[1] = (y[1] + np.pi) % (2 * np.pi) - np.pi
        return y