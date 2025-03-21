from datetime import datetime
from filterpy.kalman import KalmanFilter
import numpy as np
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag

class Kinematic:
    
    def __init__(self, observation_noise):
        self.position = (0,0)
        self.velocity = (0,0)
        self.timestamp = datetime.now()
        self.error = None
        self.delta_t = 0
        self.observation_noise = observation_noise
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
        P = (10000, 10000, 10000, 10000)
        kf.P *= np.diag(P)
        kf.R = np.array([[self.observation_noise, 0],
                         [0, self.observation_noise]
                         ])
        
        q = Q_discrete_white_noise(dim=2, dt=self.delta_t, var=0.0000013)
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
        q = Q_discrete_white_noise(dim=2, dt=self.delta_t, var=0.013)
        self.kf.Q = block_diag(q, q)
        self.kf.F[0][1] = self.delta_t
        self.kf.F[2][3] = self.delta_t
        x, y, vx, vy = self.apply_kalman_filter(estimated_x, estimated_y)
        self.position = (x, y)
        self.velocity = (vx * 1.94384, vy * 1.94384)
        self.timestamp = timestamp_now

    def linear_estimation(self, vx, vy, delta_t):
        vx = vx / 1.944
        vy = vy / 1.944
        x = self.position[0]
        y = self.position[1]
        x = x + (vx * delta_t)
        y = y + (vy * delta_t)
        self.position = (x,y)
        self.velocity = (vx,vy)