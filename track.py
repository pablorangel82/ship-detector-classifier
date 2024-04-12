import math
import uuid
from datetime import datetime
import pyproj as proj
import utm


class Track:
    uuid = ''
    name = None
    lat = None
    lon = None
    course = None
    speed = None
    category = ''
    category_index = 5
    bbox = []
    timestamp = 0
    classification_confidence = 0
    detection_confidence = 0
    votes = [0, 0, 0, 0, 0, 0]

    def __init__(self, detection_confidence, classification_confidence, categories, category_index, bbox, sensor, pixel_height):
        self.uuid = 'UUID-EN-CAMERA-' + str(uuid.uuid4())
        self.update(detection_confidence, classification_confidence, categories, category_index, bbox, sensor, pixel_height)
        self.votes = [0, 0, 0, 0, 0, 0]

    def update(self, detection_confidence, classification_confidence, categories, category_index, bbox, sensor, pixel_height):
        self.votes[category_index] += 1
        most_voted = 0
        for i in range(len(self.votes)):
            if self.votes[i] > self.votes[most_voted]:
                most_voted = i
        print(self.uuid)
        print(self.votes)
        self.category = categories[most_voted]
        self.detection_confidence = detection_confidence
        if category_index == most_voted:
            if classification_confidence > self.classification_confidence:
                self.classification_confidence = classification_confidence
        self.category_index = most_voted
        print(self.category)

        self.update_kinematics(bbox, sensor, pixel_height)

    def update_kinematics(self, bbox, sensor, pixel_height):
        self.bbox = bbox

        distance = (sensor.calibration_real_height * sensor.focal_length) / pixel_height
        distance = distance / 1000  # mm to m
        center_pixel_x = bbox[0] + int(bbox[2] / 2)
        center_pixel_y = bbox[1] + int(bbox[3] / 2)
        bearing_pixel = math.atan2((center_pixel_x), (center_pixel_y))
        bearing_pixel += math.pi
        bearing_pixel = math.degrees(bearing_pixel)
        bearing_pixel = 180 + bearing_pixel
        if bearing_pixel > 360:
            bearing_pixel = bearing_pixel - 360

        if bearing_pixel >= 270:
            bearing_pixel = 360 - bearing_pixel

        percent = bearing_pixel / 180
        bearing = sensor.bearing * percent
        self.timestamp = datetime.now()

        old_x, old_y = self.get_xy_coordinate()
        new_x, new_y = self.convert_to_xy_coordinate(bearing, distance)
        xysensor = sensor.get_xy_coordinate()
        self.convert_to_geo_coordinate(xysensor[0]+new_x, xysensor[1]+new_y)

        if old_x is not None and old_y is not None:
            distance_moved_x = (old_x - xysensor[0]+new_x)/1852
            distance_moved_y = (old_y - xysensor[1]+new_y)/1852
            distance_moved = (math.sqrt((distance_moved_x ** 2) + (distance_moved_y ** 2)))/1852
            now = datetime.now()
            time_elapsed = now - self.timestamp
            hours = time_elapsed.microseconds / 3.6e+9
            velocx = distance_moved_x / hours
            velocy = distance_moved_y / hours
            self.course = math.atan2(velocx, velocy)
            self.speed = distance_moved / hours

    def get_pixel_coordinates(self):
        return self.bbox

    def get_pixel_center_position(self):
        center_x = self.bbox[0] + int(self.bbox[2] / 2)
        center_y = self.bbox[1] + int(self.bbox[3] / 2)
        return center_x, center_y

    def get_geo_coordinate(self):
        return [self.lat, self.lon]

    def get_xy_coordinate(self):
        if self.lat is None or self.lon is None:
            return None,None
        p = proj.Proj(proj='utm', zone=23, ellps='WGS84', preserve_units=False)
        x, y = p(self.lon, self.lat)
        return [x, y]

    def get_polar_coordinate(self, reference):
        xy_ref = reference.get_xy_coordinate()
        xy = self.get_xy_coordinate()

        distance = math.sqrt(math.pow(xy_ref[0] - xy[0], 2) + math.pow(xy_ref[1] - xy[1], 2))
        distance = distance / 1852
        bearing = math.atan2((xy_ref[0] - xy[0]), (xy_ref[1] - xy[1]))
        bearing += math.pi
        bearing = math.degrees(bearing)
        bearing = 180 + bearing
        if bearing > 360:
            bearing = bearing - 360
        return bearing, distance

    def convert_to_geo_coordinate(self, x, y):
        p = proj.Proj(proj='utm',zone=23,ellps='WGS84', preserve_units=False)  # assuming you're using WGS84 geographic
        lon,lat = p(x,y, inverse=True)
        self.lat = lat
        self.lon = lon

    def convert_to_xy_coordinate(self, bearing, distance):
        x = math.sin(math.radians(bearing) * distance)
        y = math.cos(math.radians(bearing) * distance)
        return x, y

    def get_description(self):
        return self.get_name() + ' - ' + self.category.upper() + ' (' + str(round(self.classification_confidence * 100)) + ')'

    def get_name(self):
        name = '?'
        if self.name is None:
            name = self.uuid[len(self.uuid) - 3] + self.uuid[len(self.uuid) - 2] + self.uuid[len(self.uuid) - 1]
        return name

    def get_kinematics_description(self):
        description = '?'
        if self.lat is not None and self.lon is not None:
            description = 'POS: ' + str(self.lat) + ', ' + str(self.lon)
        if self.speed is not None:
            description = description + '\nSPD: ' + str(self.speed)
        if self.course is not None:
            description = description + '\nCOG: ' + str(self.course)
        return description