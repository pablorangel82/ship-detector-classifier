from imutils.video import VideoStream
import math

class Camera:

    def __init__(self, site):
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
        self.ref_bearing = camera_data['standard_bearing']
        self.zoom_min = camera_data['zoom_min']
        self.zoom_max = camera_data['zoom_max']
        
        self.height_resolution = camera_data['height_resolution']
        self.width_resolution = camera_data['width_resolution']
        self.ratio = self.height_resolution / self.width_resolution
        self.hfov_max = math.radians(camera_data['hfov_max'])
        self.hfov_min = math.radians(camera_data['hfov_min'])
        self.tilt_range = camera_data['tilt_range']
        self.pan_range = camera_data['pan_range']
        self.frame_rate = camera_data['frame_rate']

    def next_frame(self):
        (ok, frame) = self.video_stream.stream.stream.read()
        return frame

    def set_to_track_position (self, bearing, azimuth, physical_zoom):
        p = 0
        t = 0
        z = 0
        bearing = (360 - self.ref_bearing) + bearing
        if bearing > 360:
            bearing = bearing - 360
        if bearing < 180:
            p = bearing / 180
        else:
            p = ((360 - bearing) / 180) * -1
        z  = (physical_zoom - self.zoom_min) / (self.zoom_max - self.zoom_min)
        
        self.set_ptz(p,t,z)

    def set_ptz(self, pan, tilt, zoom):
        bearing = 0
        if pan > 0:
            bearing = pan * (self.pan_range / 2)
        else:
            bearing = self.pan_range - ((self.pan_range/2)) * (pan * -1)
        bearing = bearing + self.ref_bearing
        if bearing > 360:
            bearing = bearing - 360
        self.bearing = bearing
        self.physical_zoom = (self.zoom_max - self.zoom_min) * zoom
        self.azimuth = 0
        self.pan = pan
        self.tilt = tilt
        self.zoom = zoom
        self.calculate_new_focal_length(self.zoom)
    
    def calculate_new_focal_length(self,zoom):
        self.hfov = self.hfov_max - ( (self.hfov_max - self.hfov_min) * zoom)
        self.vfov = 2 * (math.atan(self.ratio * math.tan(self.hfov/2)))
        self.focal_length = self.height_resolution / (2 * math.tan(self.vfov/2)) 
