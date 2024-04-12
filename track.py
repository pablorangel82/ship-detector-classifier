import math
import uuid
from datetime import datetime
import pyproj as proj
import utm


class Track:
    uuid = ''
    name = None
    lat = 0
    lon = 0
    course = 0
    speed = 0
    category = ''
    category_index = 5
    bbox = []
    timestamp = 0
    confidence = 0
    votes = [0, 0, 0, 0, 0, 0]

    def __init__(self, confidence, categories, category_index, bbox):
        self.uuid = 'UUID-EN-CAMERA-' + str(uuid.uuid4())
        self.update(confidence, categories, category_index, bbox)
        self.votes = [0, 0, 0, 0, 0, 0]

    def update(self, confidence, categories, category_index, bbox):
        self.votes[category_index] += 1
        most_voted = 0
        for i in range(len(self.votes)):
            if self.votes[i] > self.votes[most_voted]:
                most_voted = i
        # print(self.uuid)
        # print(self.votes)
        self.category = categories[most_voted]
        self.category_index = most_voted
        if category_index == most_voted:
            if confidence > self.confidence:
                self.confidence = confidence
        else:
            self.confidence = confidence
        # print(self.category)

        self.update_bbox(bbox)

    def update_bbox(self, bbox):
        self.bbox = bbox
        self.timestamp = datetime.now()

    def get_pixel_coordinates(self):
        return self.bbox

    def get_pixel_center_position(self):
        center_x = self.bbox[0] + int(self.bbox[2] / 2)
        center_y = self.bbox[1] + int(self.bbox[3] / 2)
        return center_x, center_y

    def get_geo_coordinate(self):
        return [self.lat, self.lon]

    def get_xy_coordinate(self):
        crs_wgs = proj.Proj(init='epsg:4326')  # assuming you're using WGS84 geographic
        crs_bng = proj.Proj(init='epsg:27700')  # use a locally appropriate projected CRS

        # then cast your geographic coordinate pair to the projected system
        x, y = proj.transform(crs_wgs, crs_bng, self.lon, self.lat)
        return utm.from_latlon(self.lat, self.lon)

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

    def get_description(self):
        return self.get_name() + ' - ' + self.category.upper() + ' (' + str(round(self.confidence * 100)) + ')'

    def get_name(self):
        name = '?'
        if self.name is None:
            name = self.uuid[len(self.uuid) - 3] + self.uuid[len(self.uuid) - 2] + self.uuid[len(self.uuid) - 1]
        return name
