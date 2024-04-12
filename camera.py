import math
import utm


class Camera:
    lat = -22.912759833
    lon = -431582615
    ptz = [0, 0, 0]
    zoom_min = 4.3 #milimeters
    zoom_max = 129 #milimeters
    tilt_min = -90 #degrees
    tilt_max = 90 #degrees
    pan_min = -90 #degrees
    pan_max = 90 #degrees
    capture_rate = 60 #frame per second

    def get_xy_position(self):
        xy = utm.from_latlon(self.lat, self.lon)
        return xy



