from imutils.video import VideoStream

class Camera:
    address = ''
    lat = 0
    lon = 0
    ref_bearing = 0
    ptz = [0, 0, 0]
    zoom_min = 0
    zoom_max = 0
    tilt_min = 0
    tilt_max = 0
    pan_min = 0
    pan_max = 0
    capture_rate = 0
    focal_length = 0
    bearing = 6
    video_stream = None
    resolution_width = 0
    resolution_height = 0

    def __init__(self, location, calibration):
        self.load_config(location)
        self.focal_length = (calibration.pixel_height * calibration.real_distance) / calibration.real_height
        self.video_stream = VideoStream(self.address).start()

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
        self.capture_rate = camera_data['capture_rate']
        self.resolution_width = camera_data['resolution_width']
        self.resolution_height = camera_data['resolution_height']