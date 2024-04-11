import math
import utm


class Camera:
    lat = 0
    lon = 0
    x = 0
    y = 0
    ptz = [0, 0, 0]

    def __init__(self, lat, lon, ptz):
        self.ptz = ptz
        if lat is not None and lon is not None:
            self.lat = lat
            self.lon = lon
            xy = utm.from_latlon(lat, lon)
            self.x = xy[0]
            self.y = xy[1]

    def geo_to_polar_coordinate(self, track_lat, track_lon):
        track_xy = utm.from_latlon(track_lat, track_lon)
        return self.xy_to_polar_coordinate(track_xy)

    def xy_to_polar_coordinate(self, track_xy):
        distance = math.sqrt(math.pow(self.x - track_xy[0], 2) + math.pow(self.y - track_xy[1], 2))
        distance = distance / 1852
        bearing = math.atan2((track_xy[0]-self.x), (track_xy[1]-self.y))
        bearing += math.pi
        bearing = math.degrees(bearing)
        bearing = 180 + bearing
        if bearing > 360:
            bearing = bearing - 360
        return bearing, distance


