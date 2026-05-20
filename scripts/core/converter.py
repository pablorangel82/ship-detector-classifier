import math
from pyproj import proj

class Converter():
    
    @staticmethod
    def polar_to_xy(ref_x, ref_y, theta, r):
        x = math.sin(math.radians(theta)) * r
        y = math.cos(math.radians(theta)) * r
        if ref_x is not None and ref_y is not None:
            x = ref_x + x
            y = ref_y + y
        return x, y

    @staticmethod
    def polar_to_geo(ref_lat, ref_lon, theta, r):
        ref_x, ref_y = Converter.geo_to_xy(ref_lat, ref_lon)
        x, y = Converter.polar_to_xy(ref_x, ref_y, theta, r)
        return Converter.xy_to_geo(x, y)

    @staticmethod
    def geo_to_polar(ref_lat, ref_lon, lat, lon):
        ref_x, ref_y = Converter.geo_to_xy(ref_lat, ref_lon)
        x, y = Converter.geo_to_xy(lat, lon)
        return Converter.xy_to_polar(ref_x, ref_y, x, y)

    @staticmethod
    def xy_to_polar(ref_x, ref_y, x, y):
        if ref_x is None or ref_y is None:
            dx = x
            dy = y
        else:
            dx = x - ref_x
            dy = y - ref_y
        r = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
        theta = math.degrees(math.atan2(dx, dy)) 
        theta = (theta + 360) % 360 
        return theta, r

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
        course, speed = Converter.xy_to_polar(None, None, vx, vy)
        return speed, course

    def polar_to_geometric(theta_polar_rad):
        x_n = math.sin(theta_polar_rad)
        y_n = math.cos(theta_polar_rad)
        x_g = -x_n
        y_g = y_n

        return math.atan2(y_g, x_g)
        
    @staticmethod
    def geometric_to_polar_degrees(theta_geom_rad):
        theta_sensor = math.pi/2 - theta_geom_rad
        theta_sensor = theta_sensor % (2*math.pi)
        return math.degrees(theta_sensor)
    
    @staticmethod
    def antihorario_para_horario_xy(x, y):
        return x, -y
