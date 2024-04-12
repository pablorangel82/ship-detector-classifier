import csv
import math
import utm
import pyproj as proj


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
    calibration_pixel_height = 0
    calibration_real_height = 0
    calibration_real_distance = 0
    focal_length = 0
    bearing = 45

    def __init__(self, location):
        self.load_config(location)
        self.focal_length = (self.calibration_pixel_width * self.calibration_real_distance) / self.calibration_real_height

    def load_config(self, location):
        with (open('cameras/'+location+'.csv', 'r') as csvfile):
            config = csv.reader(csvfile, delimiter=',')
            next(config)  # skipping header
            for row in config:
                self.address = row[0]
                self.lat = float(row[1])
                self.lon = float(row[2])
                self.ref_bearing = float(row[3])
                self.zoom_min = float(row[4])
                self.zoom_max = float(row [5])
                self.tilt_min = float(row[6])
                self.tilt_max = float(row[7])
                self.pan_min = float(row[8])
                self.pan_max = float(row[9])
                self.capture_rate = float(row[10])
                self.calibration_pixel_width = float(row[11])
                self.calibration_real_height = float(row[12])
                self.calibration_real_distance = float(row[13])

    def get_xy_coordinate(self):
        if self.lat is None or self.lon is None:
            return None, None
        p = proj.Proj(proj='utm', zone=23, ellps='WGS84', preserve_units=False)
        x, y = p(self.lon, self.lat)
        return [x, y]
