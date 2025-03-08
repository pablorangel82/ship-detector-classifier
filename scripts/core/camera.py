from imutils.video import VideoStream
import math
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s', )

class Camera:

    def __init__(self, site):
        self.load_config(site)
        self.set_to_track_position(self.initial_bearing,0,self.initial_zoom)
        if self.address is not None:
            self.video_stream = VideoStream(self.address, frame_rate=self.frame_rate,
                                        resolution=(self.width_resolution, self.height_resolution))

    def load_config(self, camera_data):
        self.id = camera_data['id']
        self.address = camera_data['address']
        self.lat = camera_data['latitude']
        self.lon = camera_data['longitude']
        self.ref_bearing = camera_data['standard_bearing']
        self.initial_bearing = camera_data['initial_bearing']
        self.initial_zoom = camera_data['initial_zoom']
        self.bearing = self.initial_bearing
        self.physical_zoom = self.initial_zoom
        self.azimuth = 0
        self.zoom = 0
        self.pan = 0
        self.tilt = 0
        self.zoom = 0
        self.zoom_min = camera_data['zoom_min']
        self.zoom_max = camera_data['zoom_max']
        self.height_resolution = camera_data['height_resolution']
        self.width_resolution = camera_data['width_resolution']
        self.height_sensor = camera_data['height_sensor']
        self.width_sensor = camera_data['width_sensor']
        self.automatic_yaw_inc = (camera_data['simulation'])['automatic_yaw_inc']
        self.auto_tracking_enabled = True if (camera_data['simulation'])['auto_tracking'] == 'Enabled' else False 
        self.resolution_ratio = self.width_resolution / self.height_resolution
        self.sensor_ratio = self.width_sensor / self.height_sensor
        self.hfov_max = math.radians(camera_data['hfov_max'])
        self.hfov_min = math.radians(camera_data['hfov_min'])
        self.tilt_range = camera_data['tilt_range']
        self.pan_range = camera_data['pan_range']
        self.frame_rate = camera_data['frame_rate']
        self.interval_measured = 0.0
        self.last_yaw_inc = 0
        self.timestamp = datetime.now()
        
        logging.info('Geo Position: ' + str(self.lat) + '  ' + str(self.lon))
        if self.address is not None:
            logging.info('Address: ' + self.address)
        logging.info('Initial bearing: ' + str(self.bearing))
        logging.info('Initial zoom: ' + str(self.physical_zoom))
        logging.info('Initial Azimuth: ' + str(self.azimuth))
        logging.info('Reference bearing: ' + str(self.ref_bearing))
        logging.info('HFOV Max: ' + str(math.degrees(self.hfov_max)))
        logging.info('HFOV Min: ' + str(math.degrees(self.hfov_min)))
        logging.info('Zoom Max: ' + str(self.zoom_max))
        logging.info('Zoom Min: ' + str(self.zoom_min))
        logging.info('PAN Range: ' + str(self.pan_range))
        logging.info('Tilt Range: ' + str(self.tilt_range))
        logging.info('Frame Rate: ' + str(self.frame_rate))
        logging.info('Autotracking: ' + str(self.auto_tracking_enabled))
        logging.info('Resolution - Ratio: (' + str(self.width_resolution) + ',' + str(self.height_resolution) + ') - (' + str(self.resolution_ratio)+ ')') 
        logging.info('Sensor Dimensions - Ratio: (' + str(self.width_sensor) + ',' + str(self.height_sensor) + ') - (' + str(self.sensor_ratio)+ ')')


    def next_frame(self):
        (ok, frame) = self.video_stream.stream.stream.read()
        previous_timestamp = self.timestamp
        self.timestamp = datetime.now()
        
        self.interval_measured = (self.timestamp - previous_timestamp).microseconds / 1e+6
        if self.auto_tracking_enabled:
            self.last_yaw_inc += self.interval_measured 
            if self.last_yaw_inc >= 1:
                self.last_yaw_inc = 0
                bearing = self.bearing + self.automatic_yaw_inc
                self.set_to_track_position(bearing,0,self.physical_zoom)
        return frame

    def set_to_track_position (self, bearing, azimuth, physical_zoom):
        p = 0
        t = 0
        z = 0
        bearing = bearing + (360 - self.ref_bearing)
        if bearing >= 360:
            bearing = bearing - 360
        if bearing < 180:
            p = bearing / 180
        else:
            p = ((360 - bearing) / 180) * -1
        z  = 1- ( (physical_zoom - self.zoom_min) / (self.zoom_max - self.zoom_min))
        self.set_ptz(p,t,z)

    def set_ptz(self, pan, tilt, zoom):
        bearing = 0
        if pan > 0:
            bearing = pan * (self.pan_range / 2)
        else:
            bearing = self.pan_range - ((self.pan_range/2) * (pan * -1))
        bearing = self.ref_bearing + bearing
        if bearing >= 360:
            bearing = bearing - 360
        self.bearing = bearing
        self.physical_zoom = self.zoom_max + ((self.zoom_max - self.zoom_min) * zoom)
        self.azimuth = 0
        self.pan = pan
        self.tilt = tilt
        self.zoom = zoom
        self.calculate_new_focal_length(self.zoom)
    
    def calculate_new_focal_length(self,zoom):
        self.hfov = self.hfov_min + ((self.hfov_max - self.hfov_min) * zoom)
        self.vfov = 2 * (math.atan(self.sensor_ratio * math.tan(self.hfov/2)))
        self.focal_length_mm = self.height_sensor / (2 * math.tan(self.vfov/2)) 
        self.focal_length_px = (self.focal_length_mm * self.height_resolution) / self.height_sensor
