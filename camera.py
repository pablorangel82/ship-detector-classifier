from imutils.video import VideoStream
import datetime

class Camera:

    def __init__(self, location, calibration):
        self.estimation_interval = 10
        self.time_of_first_read = datetime.datetime.now()
        self.frames_read = 0
        self.address = None
        self.lat = None
        self.lon = None
        self.ref_bearing = None
        self.zoom_min = None
        self.zoom_max = None
        self.tilt_min = None
        self.tilt_max = None
        self.pan_min = None
        self.pan_max = None
        self.frame_rate = None
        self.resolution_width = None
        self.resolution_height = None
        self.zoom = 0
        self.bearing = 6
        self.load_config(location)
        self.focal_length = calibration.zoom * ( (calibration.pixel_height * calibration.real_distance) / calibration.real_height)
        self.video_stream = VideoStream(self.address, frame_rate=self.frame_rate,
                                        resolution=(self.resolution_width, self.resolution_height))

    def load_config(self, camera_data):
        self.address = camera_data['address']
        self.lat = camera_data['latitude']
        self.lon = camera_data['longitude']
        self.ref_bearing = camera_data['standard_bearing']
        self.zoom_min = camera_data['zoom_min']
        self.zoom_max = camera_data['zoom_max']
        self.tilt_min = camera_data['tilt_min']
        self.tilt_max = camera_data['tilt_max']
        self.pan_min = camera_data['pan_min']
        self.pan_max = camera_data['pan_max']
        self.frame_rate = camera_data['frame_rate']
        self.resolution_width = camera_data['resolution_width']
        self.resolution_height = camera_data['resolution_height']

    def next_frame(self):
        (ok, frame) = self.video_stream.stream.stream.read()
        return frame

    def set_ptz(self,pan, tilt, zoom):
        bearing = 0
        if pan > 0:
            bearing = pan * 180
        else:
            bearing = 360 - (180 * (pan * -1))
        bearing = bearing + self.ref_bearing
        if bearing > 360:
            bearing = bearing - 360
        self.bearing = bearing
        self.zoom = zoom


