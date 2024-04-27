from imutils.video import VideoStream
import datetime

import kinematic


class Camera:

    def __init__(self, location, calibration, estimate_frame_rate):
        self.estimation_interval = 10
        self.estimate_frame_rate = estimate_frame_rate
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
        self.bearing = 6
        self.load_config(location)
        self.focal_length = calibration.zoom * ( (calibration.pixel_height * calibration.real_distance) / calibration.real_height)
        self.video_stream = VideoStream(self.address, frame_rate=self.frame_rate,
                                        resolution=(self.resolution_width, self.resolution_height))
        kinematic.Kinematic.update_noise_function(1 / self.frame_rate)
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
        if self.estimate_frame_rate:
            self.frames_read = self.frames_read + 1
            now = datetime.datetime.now()
            time_elapsed = now - self.time_of_first_read
            if time_elapsed.seconds >= self.estimation_interval:
                self.frame_rate = self.frames_read / time_elapsed.seconds
                self.frames_read = 0
                self.time_of_first_read = now
                kinematic.Kinematic.update_noise_function(self.frame_rate)
                print('New frame rate detected: ' + str(self.frame_rate))
                self.estimation_interval = self.estimation_interval * 2
                if self.estimation_interval > 600:
                    self.estimation_interval = 600
        (ok, frame) = self.video_stream.stream.stream.read()
        return frame
