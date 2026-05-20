from datetime import datetime
from filterpy.kalman import KalmanFilter
from filterpy.kalman import ExtendedKalmanFilter
import numpy as np
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag
from scipy.stats import chi2

class LinearKinematic:

    SIMULATED_DT = None
    
    def __init__(self, measurement_noise, process_noise, initial_gain, innovation=1.0, gating= False):
        self.position = (0,0)
        self.velocity = (0,0)
        self.timestamp = datetime.now()
        self.error = None
        self.delta_t = 0
        self.measurement_noise = measurement_noise
        self.process_noise = process_noise
        self.initial_gain = initial_gain
        self.innovation = innovation
        self.kf = self.init_kalman_filter()
        self.gating = gating
        gating_confidence=0.99
        self.gating_threshold = chi2.ppf(gating_confidence, df=2)

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
        kf.R = np.eye(2) * self.measurement_noise
        
        q = Q_discrete_white_noise(dim=2, dt=self.delta_t, var=self.process_noise)
        LinearKinematic.Q = block_diag(q, q)
        return kf

   
    def apply_kalman_filter(self, x, y):
        if self.kf.x is None:
            self.kf.x = np.array([x, 0., y, 0.])
        self.kf.predict()
        z = np.array([x,y])
        
        if self.gating:
            z_pred = self.kf.H @ self.kf.x
            y_innov = z - z_pred
            S = self.kf.H @ self.kf.P @ self.kf.H.T + self.kf.R
            d2 = y_innov.T @ np.linalg.solve(S, y_innov)
            if d2 <= self.gating_threshold:
                self.kf.update(z)
            else:
                print(f"Gating rejected measurement: d2={d2:.2f} exceeds threshold {self.gating_threshold}")
                pass
        else:
            self.kf.update(z)

        x = self.kf.x[0]
        y = self.kf.x[2]
        vx = self.kf.x[1]
        vy = self.kf.x[3]


        return x, y, vx, vy
       
    def update(self, estimated_x, estimated_y):
        timestamp_now = datetime.now()
        if LinearKinematic.SIMULATED_DT is None:
            self.delta_t = (timestamp_now - self.timestamp).total_seconds()
        else:
            self.delta_t = LinearKinematic.SIMULATED_DT
        q = Q_discrete_white_noise(dim=2, dt=self.delta_t, var=self.process_noise)
        self.kf.Q = block_diag(q, q)
        self.kf.F[0][1] = self.delta_t
        self.kf.F[2][3] = self.delta_t
        
        x, y, vx, vy = self.apply_kalman_filter(estimated_x, estimated_y)
        self.kf.P *= self.innovation
        self.position = (x, y)
        self.velocity = (vx * 1.94384, vy * 1.94384)
        speed = np.sqrt(vx**2 + vy**2) * 1.94384
        if speed < 0.5:
            self.velocity = (0, 0)
            self.kf.x[1]=0
            self.kf.x[3]=0
        self.timestamp = timestamp_now
        

    def compute_aspect_ratio(bbox):
        x_min, y_min, x_max, y_max = bbox
        width = x_max - x_min
        height = y_max - y_min

        if height <= 0:
            return None

        return width / height