import math
from pyproj import proj

class Converter():
    
    @staticmethod
    def polar_to_xy(ref_x, ref_y, bearing, distance):
        x = math.sin(math.radians(bearing)) * distance
        y = math.cos(math.radians(bearing)) * distance
        if ref_x is not None and ref_y is not None:
            x = x + ref_x
            y = y + ref_y
        return x, y

    @staticmethod
    def polar_to_geo(ref_lat, ref_lon, bearing, distance):
        ref_x, ref_y = Converter.geo_to_xy(ref_lat, ref_lon)
        x, y = Converter.polar_to_xy(ref_x, ref_y, bearing, distance)
        return Converter.xy_to_geo(x, y)

    @staticmethod
    def geo_to_polar(ref_lat, ref_lon, lat, lon):
        ref_x, ref_y = Converter.geo_to_xy(ref_lat, ref_lon)
        x, y = Converter.geo_to_xy(lat, lon)
        return Converter.xy_to_polar(ref_x, ref_y, x, y)

    @staticmethod
    def xy_to_polar(ref_x, ref_y, x, y):
        if ref_x is None or ref_y is None:
            ref_x = 0
            ref_y = 0
        distance = math.sqrt(math.pow(x - ref_x, 2) + math.pow(y - ref_y, 2))
        bearing = math.atan2(x - ref_x, y - ref_y)
        bearing += math.pi
        bearing = math.degrees(bearing)
        bearing = 180 + bearing
        if bearing > 360:
            bearing = bearing - 360
        return bearing, distance

    @staticmethod
    def geo_to_xy(lat, lon):
        if lat is None or lon is None:
            return None, None
        p = proj.Proj(proj='utm', zone=23, ellps='WGS84', preserve_units=False)
        x, y = p(lon, lat)
        return x, y

    @staticmethod
    def xy_to_geo(x, y):
        if x is None or y is None:
            return None, None
        p = proj.Proj(proj='utm', zone=23, ellps='WGS84',
                      preserve_units=False)  # assuming you're using WGS84 geographic
        lon, lat = p(x, y, inverse=True)
        return lat, lon

    @staticmethod
    def euclidian_distance(x1, y1, x2, y2):
        return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

    @staticmethod
    def delta_time(it, ft):
        return (ft - it).total_seconds()

    @staticmethod
    def calculate_speed_and_course(vx, vy):
        course, speed = Converter.xy_to_polar(0, 0, vx, vy)
        return speed, course
