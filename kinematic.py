import math
from datetime import datetime
from pyproj import proj
from filterpy.kalman import KalmanFilter
import numpy as np
from filterpy.common import Q_discrete_white_noise

from GenericList import GenericList

NUMBER_OF_SAMPLES = 1


class Kinematic():
    geo_positions = None
    pixel_positions = None
    velocities = None
    kf = None
    distance_from_camera = 0
    bearing = 0
    timestamp = 0
    delta_t = 0

    def __init__(self):
        self.geo_positions = GenericList(NUMBER_OF_SAMPLES)
        self.pixel_positions = GenericList(NUMBER_OF_SAMPLES)
        self.velocities = GenericList(NUMBER_OF_SAMPLES)
        self.kf = self.init_kalman_filter()
        self.kf_vy = self.init_kalman_filter()
        self.timestamp = datetime.now()
        self.distance_from_camera = None
        self.bearing = None
        self.delta_t = 0

    def init_kalman_filter(self):
        kf = KalmanFilter(dim_x=2, dim_z=1)
        kf.alpha = 1
        kf.x = None
        kf.F = np.array([[1., 1.], [0., 1.]])
        kf.H = np.array([[1., 0.]])
        kf.P *= 1000.
        kf.R = .8
        kf.Q = Q_discrete_white_noise(dim=2, dt=1/60, var=0.13)
        return kf

    @staticmethod
    def polar_to_xy(ref_x, ref_y, bearing, distance):
        x = math.sin(math.radians(bearing)) * distance
        y = math.cos(math.radians(bearing)) * distance
        if ref_x and ref_y is not None:
            x += x + ref_x
            y += y + ref_y
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
    def calculate_speed_and_course(vx, vy, delta_t):
        course, speed = Kinematic.xy_to_polar(0, 0, vx, vy)
        return speed / delta_t, course

    def apply_kalman_filter(self, x, y):
        if self.kf.x is None:
            self.kf.x = np.array([[x, y], [0, 0]])
        self.kf.predict()
        self.kf.update(x)
        vx = self.kf.x[0]
        vy = self.kf.x[1]
        return vx, vy

    def update(self, bbox, frame_width, frame_height, camera, calibration):
        timestamp_now = datetime.now()
        bbox_added = False
        if self.pixel_positions.get_current_value() is None:
            self.pixel_positions.add_value(bbox)
            bbox_added = True
        time_elapsed = Kinematic.delta_time(self.timestamp, timestamp_now)
        if time_elapsed > self.delta_t:
            distance = calibration.zoom * (
                        (calibration.real_height * camera.focal_length) / self.get_pixel_coordinates()[3])
            distance = (distance / 1000)  # mm to m
            new_center_pixel_x = bbox[0] + int(bbox[2] / 2)
            bearing_pixel, distance_pixel = Kinematic.xy_to_polar(0, 0, new_center_pixel_x - (frame_width/2), frame_height)
            new_bearing = camera.bearing + bearing_pixel
            if new_bearing > 360:
                new_bearing = 360 - new_bearing
            new_distance = distance

            self.bearing = new_bearing
            self.distance_from_camera = new_distance
            old_position_x = 0
            old_position_y = 0
            old_position = self.geo_positions.get_current_value()
            # if old_position is not None:
            #     old_position_x = old_position[0]
            #     old_position_y = old_position[1]
            new_position_lat, new_position_lon = Kinematic.polar_to_geo(camera.lat, camera.lon, self.bearing,
                                                                    self.distance_from_camera)
            new_position_x, new_position_y = Kinematic.geo_to_xy(new_position_lat, new_position_lon)
            vx, vy = self.apply_kalman_filter(new_position_x, new_position_y)
            self.velocities.add_value([vx * 1.94384, vy * 1.94384])
            self.timestamp = timestamp_now
            self.geo_positions.add_value([new_position_x, new_position_y])
            if bbox_added is not True:
                self.pixel_positions.add_value(bbox)

    def get_pixel_coordinates(self):
        return self.pixel_positions.get_current_value()

    def get_pixel_center_position(self):
        bbox = self.get_pixel_coordinates()
        center_x = bbox[0] + int(bbox[2] / 2)
        center_y = bbox[1] + int(bbox[3] / 2)
        return center_x, center_y

    def get_current_kinematic(self):
        lat = lon = speed = course = bbox = None
        bbox = self.pixel_positions.get_current_value()
        xy = self.geo_positions.get_current_value()
        if xy is not None:
            lat, lon = Kinematic.xy_to_geo(xy[0], xy[1])
        vx_vy = self.velocities.get_current_value()
        if vx_vy is not None:
            speed, course = Kinematic.calculate_speed_and_course(vx_vy[1][0], vx_vy[1][1], 1)

        return lat, lon, speed, course, bbox

    def to_string(self):
        string = 'self.get_description()'
        lat, lon, speed, course, bbox = self.get_current_kinematic()
        if lat or lon or speed or course is None:
            return str(bbox)
        string = string + '\nPOS: ' + str(lat) + ', ' + str(lon)
        string = string + '\nSPD: ' + str(speed)
        string = string + '\nCOG: ' + str(course)
        return string
