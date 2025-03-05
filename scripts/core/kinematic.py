import math
from datetime import datetime
from pyproj import proj
from filterpy.kalman import KalmanFilter
import numpy as np
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag
from core.GenericList import GenericList

class Kinematic:
    NUMBER_OF_SAMPLES = 10
    dt = 1
    Q = None

    def __init__(self):
        self.lost = False
        self.geo_positions = GenericList(1)
        self.pixel_positions = GenericList(1)
        self.velocities = GenericList(Kinematic.NUMBER_OF_SAMPLES)
        self.kf = self.init_kalman_filter()
        self.timestamp = datetime.now()
        self.distance_from_camera = None
        self.bearing = None
        self.error = None

    def init_kalman_filter(self):
        kf = KalmanFilter(dim_x=4, dim_z=2)
        kf.alpha = 1
        kf.x = None
        kf.F = np.array([[1., Kinematic.dt, 0., 0.],
                         [0., 1., 0., 0.],
                         [0., 0., 1., Kinematic.dt],
                         [0., 0., 0., 1.]])
        kf.H = np.array([[1., 0., 0., 0.],
                         [0., 0., 1., 0.]])
        P = (10000, 10000, 10000, 10000)
        kf.P *= np.diag(P)
        kf.R = np.array([[7, 0],
                         [0, 7]
                         ])
        kf.Q = Kinematic.Q
        return kf

    @staticmethod
    def polar_to_xy(ref_x, ref_y, bearing, distance):
        x = math.sin(math.radians(bearing)) * distance
        y = math.cos(math.radians(bearing)) * distance
        if ref_x and ref_y is not None:
            x = x + ref_x
            y = y + ref_y
        return x, y

    @staticmethod
    def polar_to_geo(ref_lat, ref_lon, bearing, distance):
        ref_x, ref_y = Kinematic.geo_to_xy(ref_lat, ref_lon)
        x, y = Kinematic.polar_to_xy(ref_x, ref_y, bearing, distance)
        return Kinematic.xy_to_geo(x, y)

    @staticmethod
    def geo_to_polar(ref_lat, ref_lon, lat, lon):
        ref_x, ref_y = Kinematic.geo_to_xy(ref_lat, ref_lon)
        x, y = Kinematic.geo_to_xy(lat, lon)
        return Kinematic.xy_to_polar(ref_x, ref_y, x, y)

    @staticmethod
    def xy_to_polar(ref_x, ref_y, x, y):
        distance = math.sqrt(math.pow(x - ref_x, 2) + math.pow(y - ref_y, 2))
        bearing = math.atan2(x - ref_x, y - ref_y)
        bearing += math.pi
        bearing = math.degrees(bearing)
        bearing = 180 + bearing
        if bearing > 360:
            bearing = bearing - 360
        return bearing, distance

    @staticmethod
    def geo_to_xy(lat, lon):
        p = proj.Proj(proj='utm', zone=23, ellps='WGS84', preserve_units=False)
        x, y = p(lon, lat)
        return x, y

    @staticmethod
    def xy_to_geo(x, y):
        p = proj.Proj(proj='utm', zone=23, ellps='WGS84',
                      preserve_units=False)  # assuming you're using WGS84 geographic
        lon, lat = p(x, y, inverse=True)
        return lat, lon

    @staticmethod
    def euclidian_distance(x1, y1, x2, y2):
        return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

    @staticmethod
    def delta_time(it, ft):
        return (ft - it).total_seconds()

    @staticmethod
    def calculate_speed_and_course(vx, vy):
        course, speed = Kinematic.xy_to_polar(0, 0, vx, vy)
        return speed, course

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

    @staticmethod
    def measure_position(alpha, bearing, height):
        if alpha == 0:
            return b,math.nan
        if alpha <= 90:
            alpha = 90 - alpha
        else:
            if alpha <= 180:
                alpha = 180 - alpha
            else:
                if alpha < 270:
                    alpha = 270 - alpha
                else:
                    alpha = 360 - alpha
        alpha = math.radians(alpha)
        d=  height / math.tan(alpha)
        b = bearing
        return b,d
    
    def monocular_vision_detection(self, bbox, camera, real_height):
        self.pixel_positions.add_value(bbox)
        new_distance = ((real_height * camera.focal_length) / self.get_avg_bbox()[3])
        new_distance = (new_distance / 1000)  # mm to m
        x_center_pixel = self.get_avg_bbox()[0] + (self.get_avg_bbox()[2] / 2)
        x_center_frame = camera.width_resolution / 2
        
        new_bearing = camera.bearing
        if x_center_pixel > x_center_frame:
            fator = (x_center_pixel - (camera.width_resolution/2)) / (camera.width_resolution / 2)
            diff_degrees = fator * math.degrees(camera.hfov/2)
            new_bearing = new_bearing + diff_degrees
            if new_bearing > 360:
                new_bearing = new_bearing - 360
        else:
            fator = 1- (x_center_pixel / (camera.width_resolution/2))
            diff_degrees = fator * math.degrees(camera.hfov/2)
            new_bearing = new_bearing - diff_degrees
            if new_bearing < 0:
                new_bearing = 360 - abs(new_bearing)
        self.bearing = new_bearing
        self.distance_from_camera = new_distance
        new_position_lat, new_position_lon = Kinematic.polar_to_geo(camera.lat, camera.lon, self.bearing,
                                                                    self.distance_from_camera)
        new_position_x, new_position_y = Kinematic.geo_to_xy(new_position_lat, new_position_lon)

        return new_position_x,new_position_y
    
    def estimate(self, estimated_x, estimated_y):
        self.kf.Q = Kinematic.Q
        self.lost = False
        timestamp_now = datetime.now()
        self.kf.F[0][1] = Kinematic.dt
        self.kf.F[2][3] = Kinematic.dt
        x, y, vx, vy = self.apply_kalman_filter(estimated_x, estimated_y)
        self.velocities.add_value([vx * 1.94384, vy * 1.94384])
        self.timestamp = timestamp_now
        self.geo_positions.add_value([x, y])

    def update(self, bbox, camera, avg_air_draught):
        estimated_x, estimated_y = self.monocular_vision_detection(bbox,camera,avg_air_draught)
        self.estimate(estimated_x,estimated_y)

    def get_pixel_coordinates(self):
        return self.get_avg_bbox()

    def get_pixel_center_position(self):
        bbox = self.get_pixel_coordinates()
        center_x = bbox[0] + int(bbox[2] / 2)
        center_y = bbox[1] + int(bbox[3] / 2)
        return center_x, center_y

    def get_current_kinematic(self):
        lat = lon = speed = course = bbox = None
        bbox = self.get_pixel_coordinates()
        xy = self.geo_positions.get_current_value()
        if xy is not None:
            lat, lon = Kinematic.xy_to_geo(xy[0], xy[1])
        vx_vy = self.velocities.get_current_value()
        if vx_vy is not None:
            speed, course = Kinematic.calculate_speed_and_course(vx_vy[0], vx_vy[1])
        return lat, lon, speed, course, self.bearing, self.distance_from_camera, bbox

    def to_string(self):
        string = ''
        lat, lon, speed, course, bbox = self.get_current_kinematic()
        string = string + '\nPOS: ' + str(lat) + ', ' + str(lon)
        string = string + '\nSPD: ' + str(speed)
        string = string + '\nCOG: ' + str(course)
        return string

    @staticmethod
    def update_noise_function():
        Kinematic.dt = 0.03
        q = Q_discrete_white_noise(dim=2, dt=Kinematic.dt, var=0.0000013)
        Kinematic.Q = block_diag(q, q)

    def get_avg_bbox(self):
        avg_width = 0
        avg_height = 0
        for index in self.pixel_positions.values:
            value = self.pixel_positions.values[index]
            avg_width += value[2]
            avg_height += value[3]
        avg_width /= len(self.pixel_positions.values)
        avg_height /= len(self.pixel_positions.values)
        x = self.pixel_positions.get_current_value()[0]
        y = self.pixel_positions.get_current_value()[1]
        return x, y, avg_width, avg_height
