from imutils.video import VideoStream
import math

class Camera:

    def __init__(self, location, calibration):
        self.load_config(location)
        self.set_ptz(0.25,0,0.8)
        self.video_stream = VideoStream(self.address, frame_rate=self.frame_rate,
                                        resolution=(self.width_resolution, self.height_resolution))

    def load_config(self, camera_data):
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

    def set_ptz(self,pan, tilt, zoom):
        self.zoom = zoom
        bearing = 0
        if pan > 0:
            bearing = pan * (self.pan_range / 2)
        else:
            bearing = self.pan_range - ((self.pan_range/2)) * (pan * -1)
        bearing = bearing + self.ref_bearing
        if bearing > 360:
            bearing = bearing - 360
        self.bearing = bearing
        self.calculate_new_focal_length(zoom)
    
    def calculate_new_focal_length(self,zoom):
        self.hfov = self.hfov_max - ( (self.hfov_max - self.hfov_min) * zoom)
        self.vfov = 2 * (math.atan(self.ratio * math.tan(self.hfov/2)))
        self.focal_length = self.height_resolution / (2 * math.tan(self.vfov/2)) 
        