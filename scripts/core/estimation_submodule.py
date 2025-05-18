from datetime import datetime
from filterpy.kalman import KalmanFilter
import numpy as np
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag

class Kinematic:

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
        Kinematic.Q = block_diag(q, q)
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
        if Kinematic.SIMULATED_DT is None:
            self.delta_t = (timestamp_now - self.timestamp).microseconds / 1e+6
        else:
            self.delta_t = Kinematic.SIMULATED_DT
        q = Q_discrete_white_noise(dim=2, dt=self.delta_t, var=self.process_noise)
        self.kf.Q = block_diag(q, q)
        self.kf.F[0][1] = self.delta_t
        self.kf.F[2][3] = self.delta_t
        x, y, vx, vy = self.apply_kalman_filter(estimated_x, estimated_y)
        self.position = (x, y)
        self.velocity = (vx * 1.94384, vy * 1.94384)
        self.timestamp = timestamp_now
        
