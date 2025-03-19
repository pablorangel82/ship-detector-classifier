import time
from imutils.video import VideoStream
import math
from datetime import datetime
import logging
from core.converter import Converter

logging.basicConfig(level=logging.INFO, format='%(message)s', )

class Camera:

    def __init__(self, site):
        self.focused_track = None
        self.load_config(site)
        self.set_ptz(0.24,0.02,0.541804433)
        if self.address is not None:
            self.video_stream = VideoStream(self.address, frame_rate=self.frame_rate,
                                        resolution=(self.width_resolution, self.height_resolution))

    def load_config(self, camera_data):
        self.id = camera_data['id']
        self.address = camera_data['address']
        self.lat = camera_data['latitude']
        self.lon = camera_data['longitude']
        self.ref_altitude = camera_data['reference_altitude']
        self.ref_azimuth = camera_data['reference_azimuth']
        self.installation_height = camera_data['installation_height']
        self.surveillance_radius = camera_data ['surveillance_radius']
        self.sensor_height = camera_data ['sensor_height']
        self.sensor_width = camera_data ['sensor_width']
        self.zoom_multiplier_min = camera_data['zoom_multiplier_min']
        self.zoom_multiplier_max = camera_data['zoom_multiplier_max']
        self.zoom_lens_min = camera_data['zoom_lens_min']
        self.zoom_lens_max = camera_data['zoom_lens_max']
        self.height_resolution = camera_data['height_resolution']
        self.width_resolution = camera_data['width_resolution']
        self.frame_rate = camera_data['frame_rate']
        self.bearing = 0
        self.zoom_multiplier = self.zoom_multiplier_min
        self.pan = 0
        self.tilt = 0
        self.zoom = 0
        self.focused_track = None
        self.resolution_ratio = self.width_resolution / self.height_resolution
        self.interval_measured = 0.0
        self.timestamp = datetime.now()
        self.timestamp_ptz = datetime.now()
        logging.info('Geo Position: ' + str(self.lat) + '  ' + str(self.lon))
        if self.address is not None:
            logging.info('Address: ' + self.address)
        logging.info('Reference altitude (degrees): ' + str(self.ref_altitude))
        logging.info('Reference azimuth (degrees): ' + str(self.ref_azimuth))
        logging.info('Initial Bearing (degrees): ' + str(self.bearing))
        logging.info('Initial zoom (multiplier): ' + str(self.zoom_multiplier))
        logging.info('Installation height (m): ' + str(self.installation_height))
        logging.info('Surveillance Radius (m): ' + str(self.surveillance_radius))
        logging.info('Sensor Width (degrees): ' + str(self.sensor_width))
        logging.info('Sensor Height (degrees): ' + str(self.sensor_height))
        logging.info('Zoom Max (multiplier): ' + str(self.zoom_multiplier_max))
        logging.info('Zoom Min (multiplier): ' + str(self.zoom_multiplier_min))
        logging.info('Zoom Lens (mm): ' + str(self.zoom_lens_max))
        logging.info('Zoom Min (mm): ' + str(self.zoom_lens_min))
        logging.info('Frame Rate (FPS): ' + str(self.frame_rate))
        logging.info('Resolution - Ratio: (' + str(self.width_resolution) + ',' + str(self.height_resolution) + ') - (' + str(self.resolution_ratio)+ ')') 
       
    def next_frame(self):
        (ok, frame) = self.video_stream.stream.stream.read()
        previous_timestamp = self.timestamp
        self.timestamp = datetime.now()
        self.interval_measured = (self.timestamp - previous_timestamp).microseconds / 1e+6
        return frame
    
    def tracking(self, track):
        x, y = Converter.geo_to_xy(track.lat, track.lon)
        track.utm.position = (x, y)
        previous_timestamp = self.timestamp_ptz
        self.timestamp_ptz = datetime.now()
        interval = (self.timestamp_ptz - previous_timestamp).seconds
        
        vx, vy = Converter.polar_to_xy(0,0,track.course,track.speed)
        track.utm.linear_estimation(vx, vy, interval)
        track.lat, track.lon = Converter.xy_to_geo(track.utm.position[0],track.utm.position[1])
        bearing, distance = Converter.geo_to_polar(self.lat,self.lon,track.lat,track.lon)
        
        print('\n')
        print(f'Bearing: {bearing}')
        print(f'Distance: {distance}')
        
        self.set_to_track_position(bearing,distance)
        
    def set_to_track_position (self, bearing, distance):
        p = 0
        t = 0
        z = 0

        if (self.installation_height + distance) > self.surveillance_radius:
            self.zoom_multiplier = self.zoom_multiplier_max
        else:
            self.zoom_multiplier = ((self.installation_height + distance) / self.surveillance_radius) * self.zoom_x_max
        z  = (self.zoom_multiplier - self.zoom_multiplier_min) / (self.zoom_multiplier_max - self.zoom_multiplier_min)
            
   
        theta = math.atan2(self.installation_height, distance)
        theta += math.pi
        theta = math.degrees(theta)
        theta += self.ref_altitude
        if theta > 360:
            theta = theta - 360
        
        if theta > 180:
            t = 180 / theta 
            t = 1-t
         
        else:
            t = theta / 180
            t = (1- t)*-1

        bearing = bearing + (360 - self.ref_azimuth)
        if bearing >= 360:
            bearing = bearing - 360
        self.bearing = bearing
        if bearing < 180:
            p = bearing / 180
        else:
            p = ((360 - bearing) / 180) * -1
        
        self.set_ptz(p,t,z)

    def convert_ptz_to_polar(self, pan, tilt, zoom):
        if pan >= 0:
            bearing = pan * 180
        else:
            bearing = 360 - ((pan*-1) * 180)
        self.bearing = bearing

        self.zoom_multiplier = (self.zoom_multiplier_max - self.zoom_multiplier_min) * zoom

        self.zoom = zoom
        self.tilt = tilt
        self.pan = pan

        self.calculate_new_focal_length(1-self.zoom)

    def set_ptz(self, pan, tilt, zoom):
        self.pan = pan
        self.tilt = tilt
        self.zoom = zoom
      
        self.calculate_new_focal_length(1-self.zoom)
    
    def calculate_new_focal_length(self,zoom):
        self.focal_length_mm = self.zoom_lens_min + ((self.zoom_lens_max - self.zoom_lens_min) * zoom)
        self.hfov = 2 * (math.atan(self.sensor_width/(2*self.focal_length_mm)))
        self.focal_length_px = (self.focal_length_mm * self.height_resolution) / self.sensor_height
