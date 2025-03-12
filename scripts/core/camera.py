from imutils.video import VideoStream
import math
from datetime import datetime
import logging
from core.track import Track
from core.converter import Converter

logging.basicConfig(level=logging.INFO, format='%(message)s', )

class Camera:

    def __init__(self, site):
        self.focused_track = None
        self.load_config(site)
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
        self.physical_zoom = camera_data['initial_zoom']
        self.installation_height = camera_data['installation_height']
        self.surveillance_radius = camera_data ['surveillance_radius']
        self.bearing = self.initial_bearing
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
        self.auto_tracking_enabled = True if (camera_data['simulation'])['auto_tracking'] == 'Enabled' else False 
        self.simulation_track_estimation = True if (camera_data['simulation'])['track_estimation'] == 'Enabled' else False
        self.focused_track = Track('Simulation')
        if self.simulation_track_estimation:
            self.focused_track.lat = camera_data['simulation']['track']['latitude']
            self.focused_track.lon = camera_data['simulation']['track']['longitude']
            self.focused_track.speed = camera_data['simulation']['track']['speed']
            self.focused_track.course = camera_data['simulation']['track']['course']
            x,y=Converter.geo_to_xy(self.focused_track.lat,self.focused_track.lon)
            self.focused_track.utm.position = (x,y)
            
        self.resolution_ratio = self.width_resolution / self.height_resolution
        self.sensor_ratio = self.width_sensor / self.height_sensor
        self.hfov_max = math.radians(camera_data['hfov_max'])
        self.hfov_min = math.radians(camera_data['hfov_min'])
        self.tilt_range = camera_data['tilt_range']
        self.pan_range = camera_data['pan_range']
        self.frame_rate = camera_data['frame_rate']
        self.interval_measured = 0.0
        self.timestamp = datetime.now()
        self.tracking_status = 'untracked'
        logging.info('Geo Position: ' + str(self.lat) + '  ' + str(self.lon))
        if self.address is not None:
            logging.info('Address: ' + self.address)
        logging.info('Initial bearing: ' + str(self.bearing))
        logging.info('Initial zoom: ' + str(self.physical_zoom))
        logging.info('Reference bearing: ' + str(self.ref_bearing))
        logging.info('Installation height: ' + str(self.installation_height))
        logging.info('Surveillance Radius: ' + str(self.surveillance_radius))
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
            if self.focused_track is not None:
                if self.simulation_track_estimation:
                    self.tracking()
        return frame
    
    def tracking(self):
        if self.tracking_status == 'untracked':
            self.tracking_status = 'tracking'
        
        vx, vy = Converter.polar_to_xy(0,0,self.focused_track.course,self.focused_track.speed)
        self.focused_track.utm.linear_estimation(vx, vy, self.interval_measured)
        self.focused_track.lat, self.focused_track.lon = Converter.xy_to_geo(self.focused_track.utm.position[0],self.focused_track.utm.position[1])
        bearing, distance = Converter.geo_to_polar(self.lat,self.lon,self.focused_track.lat,self.focused_track.lon)
        self.set_to_track_position(bearing,distance)
        
    def set_to_track_position (self, bearing, distance):
        p = 0
        t = 0
        z = 0

        if self.installation_height > distance:
            t = 1
        else:
            t = self.installation_height / distance 
        if self.tracking_status == 'tracking':
            if (self.installation_height + distance) > self.surveillance_radius:
                self.physical_zoom = self.zoom_max
            else:
                self.physical_zoom = ((self.installation_height + distance) / self.surveillance_radius) * self.zoom_max
            z  = (self.physical_zoom - self.zoom_min) / (self.zoom_max - self.zoom_min)
            self.tracking_status = 'tracked'
        else:
            z = self.zoom
        
        bearing = bearing + (360 - self.ref_bearing)
        if bearing >= 360:
            bearing = bearing - 360
        self.bearing = bearing
        if bearing < 180:
            p = bearing / 180
        else:
            p = ((360 - bearing) / 180) * -1

        self.set_ptz(p,t,z)

    def set_ptz(self, pan, tilt, zoom):
        self.pan = pan
        self.tilt = tilt
        self.zoom = zoom
        #send to onvif
        self.calculate_new_focal_length(1-self.zoom)
    
    def calculate_new_focal_length(self,zoom):
        self.hfov = self.hfov_min + ((self.hfov_max - self.hfov_min) * zoom)
        self.vfov = 2 * (math.atan(self.sensor_ratio * math.tan(self.hfov/2)))
        self.focal_length_mm = self.height_sensor / (2 * math.tan(self.vfov/2)) 
        self.focal_length_px = (self.focal_length_mm * self.height_resolution) / self.height_sensor
