import time
from imutils.video import VideoStream
import math
from datetime import datetime, timezone
import logging
from core.converter import Converter

logging.basicConfig(level=logging.INFO, format='%(message)s', )

class Camera:

    def __init__(self, site):
        self.focused_track = None
        self.load_config(site)
        self.set_ptz(0,0,0)
        if self.address is not None:
            self.video_stream = VideoStream(self.address, frame_rate=self.frame_rate,
                                        resolution=(self.width_resolution, self.height_resolution))

    def load_config(self, camera_data):
        self.id = camera_data['id']
        self.address = camera_data['address']
        self.lat = camera_data['latitude']
        self.lon = camera_data['longitude']
        self.ref_elevation= camera_data['reference_elevation']
        self.ref_azimuth = camera_data['reference_azimuth']
        self.installation_height = camera_data['installation_height']
        self.surveillance_radius = camera_data ['surveillance_radius']
        self.focus_frame_view = camera_data ['focus_frame_view']
        self.sensor_height = camera_data ['sensor_height']
        self.sensor_width = camera_data ['sensor_width']
        self.zoom_multiplier_min = camera_data['zoom_multiplier_min']
        self.zoom_multiplier_max = camera_data['zoom_multiplier_max']
        self.zoom_lens_min = camera_data['zoom_lens_min']
        self.zoom_lens_max = camera_data['zoom_lens_max']
        self.hfov_min = camera_data['hfov_min']
        self.hfov_max = camera_data['hfov_max']
        self.height_resolution = camera_data['height_resolution']
        self.width_resolution = camera_data['width_resolution']
        self.frame_rate = camera_data['frame_rate']
        self.bearing = 0
        self.elevation = 0
        self.zoom_multiplier = self.zoom_multiplier_min
        self.pan = 0
        self.tilt = 0
        self.zoom = 0
        self.manual_offset_pan = 0
        self.manual_offset_tilt = 0
        self.manual_offset_zoom = 0
        self.focused_track = None
        self.resolution_ratio = self.width_resolution / self.height_resolution
        self.interval_measured = 0.0
        self.timestamp = datetime.now()
        self.timestamp_ptz = datetime.now()
        
        if self.address is not None:
            logging.info('Address: ' + self.address)
        logging.info('Geo Position: ' + str(self.lat) + '  ' + str(self.lon))
        logging.info('Reference elevation (degrees): ' + str(self.ref_elevation))
        logging.info('Reference azimuth (degrees): ' + str(self.ref_azimuth))
        logging.info('Initial Bearing (degrees): ' + str(self.bearing))
        logging.info('Initial zoom (multiplier): ' + str(self.zoom_multiplier))
        logging.info('Installation height (m): ' + str(self.installation_height))
        logging.info('Surveillance Radius (m): ' + str(self.surveillance_radius))
        logging.info('Focus Frame View (px): ' + str(self.focus_frame_view))
        logging.info('Sensor Width (degrees): ' + str(self.sensor_width))
        logging.info('Sensor Height (degrees): ' + str(self.sensor_height))
        logging.info('Zoom Max (multiplier): ' + str(self.zoom_multiplier_max))
        logging.info('Zoom Min (multiplier): ' + str(self.zoom_multiplier_min))
        logging.info('Zoom Lens Max (mm): ' + str(self.zoom_lens_max))
        logging.info('Zoom Lens Min (mm): ' + str(self.zoom_lens_min))
        logging.info('HFOV Min (degrees): ' + str(self.hfov_max))
        logging.info('HFOV Max (degrees): ' + str(self.hfov_min))
        logging.info('Frame Rate (FPS): ' + str(self.frame_rate))
        logging.info('Resolution - Ratio: (' + str(self.width_resolution) + ',' + str(self.height_resolution) + ') - (' + str(self.resolution_ratio)+ ')') 
       
    def next_frame(self):
        (ok, frame) = self.video_stream.stream.stream.read()
        previous_timestamp = self.timestamp
        self.timestamp = datetime.now()
        self.interval_measured = (self.timestamp - previous_timestamp).microseconds / 1e+6
        return frame
    
    def tracking(self, track, offset):
        x, y = Converter.geo_to_xy(track.lat, track.lon)
        track.utm.position = (x, y)
        #logging.info(f'Xp: {track.utm.position[0]}')
        #logging.info(f'Yp: {track.utm.position[1]}')
        track.utm.timestamp = datetime.now(timezone.utc)
        interval = (track.utm.timestamp - self.timestamp_ptz).seconds
        interval += 5
        
        vx, vy = Converter.polar_to_xy(None,None,track.course,track.speed)
        track.utm.linear_estimation(vx, vy, interval)
        lat, lon = Converter.xy_to_geo(track.utm.position[0],track.utm.position[1])
        
        bearing, distance = Converter.geo_to_polar(self.lat,self.lon,lat,lon)
        
        print('\n')
        logging.info(f'Bearing: {bearing}')
        logging.info(f'Distance: {distance}')
        logging.info(f'Interval: {interval}')
        logging.info(f'Speed: {track.speed}')
        logging.info(f'Course: {track.course}')
        # logging.info(f'Track timestamp: {track.utm.timestamp}')
        # logging.info(f'Previous timestamp: {self.timestamp_ptz}')
        # logging.info(f'VX: {vx}')
        # logging.info(f'VY: {vy}')
        # logging.info(f'X: {x}')
        # logging.info(f'Y: {y}')
        print('\n')
        
        self.set_to_track_position(bearing,distance, offset)
        
    def set_to_track_position(self, bearing, distance, offset=None):
        p = 0
        t = 0
        z = 0
   
        
        z = self.estimate_zoom_factor_by_focal_estimation(distance)

        theta = math.atan2(self.installation_height, distance)
        theta += math.pi
        theta = math.degrees(theta)
        theta += self.ref_elevation
        theta = theta - 180  
        t = ((theta - (-90)) / (90 - (-90))) * 2 - 1
        t *= -1
        self.elevation = t * 90
        self.bearing = bearing
        bearing = bearing + (360 - self.ref_azimuth)
        
        if bearing >= 360:
            bearing = bearing - 360
        
        if bearing < 180:
            p = bearing / 180
        else:
            p = ((360 - bearing) / 180) * -1
        
        
        if offset is not None:
            p += float(offset.get('p'))
            t += float(offset.get('t'))
            z += float(offset.get('z'))
            
        
        self.set_ptz(p,t,z)

    def convert_ptz_to_polar(self, pan, tilt, zoom):
        if pan >= 0:
            bearing = pan * 180
        else:
            bearing = 360 - ((pan*-1) * 180)
        self.bearing = bearing
        
        self.elevation = tilt * 90
        
        self.zoom_multiplier = (self.zoom_multiplier_max - self.zoom_multiplier_min) * zoom
        self.set_ptz(pan,tilt,zoom)
        
    def set_ptz(self, pan, tilt, zoom):
        pan = pan + self.manual_offset_pan
        tilt = tilt + self.manual_offset_tilt
        zoom = zoom + self.manual_offset_zoom

        if pan > 1:
            pan = 1
        if pan < -1:
            pan = -1
        
        if tilt > 1:
            tilt = 1
        if tilt < -1:
            tilt = -1
        
        if zoom > 1:
            zoom = 1
        if zoom < 0:
            zoom = 0
        
        self.pan = pan
        self.tilt = tilt
        self.zoom = zoom

        self.calculate_new_focal_length(self.zoom)
    
    def calculate_new_focal_length(self,zoom):
        self.focal_length_mm = self.zoom_lens_min + ((self.zoom_lens_max - self.zoom_lens_min) * zoom)
        self.hfov = self.hfov_min + ((self.hfov_max - self.hfov_min) * (1-zoom))
        self.focal_length_px = (self.focal_length_mm * self.height_resolution) / self.sensor_height

    def estimate_zoom_factor_survaillance_radius(self,distance):
        if (self.installation_height + distance) > self.surveillance_radius:
            self.zoom_multiplier = self.zoom_multiplier_max
        else:
            self.zoom_multiplier = ((self.installation_height + distance) / self.surveillance_radius) * self.zoom_multiplier_max
        zoom_factor  = (self.zoom_multiplier - self.zoom_multiplier_min) / (self.zoom_multiplier_max - self.zoom_multiplier_min)
        return zoom_factor

    def estimate_zoom_factor_by_focal_estimation(self, distance):
        if distance <=0 :
            return 0
        scene_width = self.focus_frame_view * 0.2645833333
        theta = 2 * math.atan(scene_width / (2 * distance))
        required_focal_length_mm = self.sensor_width / (2 * math.tan(theta / 2))
        zoom_factor = required_focal_length_mm / self.zoom_lens_max
        return zoom_factor
    
