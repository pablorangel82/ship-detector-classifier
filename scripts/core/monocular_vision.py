import math
from core.converter import Converter

class MonocularVision():
    
    @staticmethod
    def monocular_vision_detection_method_1(alpha, bearing, height):
        if alpha == 0:
            return b,math.nan
        if alpha <= 90:
            alpha = 90 - alpha
        else:
            if alpha <= 180:
                alpha = 180 - alpha
            else:
                if alpha < 270:
                    alpha = 270 - alpha
                else:
                    alpha = 360 - alpha
        alpha = math.radians(alpha)
        d=  height / math.tan(alpha)
        b = bearing
        return b,d
    
    def monocular_vision_detection_method_2(camera, real_height, detected_bbox):
        pixel_width = detected_bbox [2]
        pixel_height = detected_bbox [3]
        
        x_center_pixel = (detected_bbox [0] + pixel_width) / 2
        x_center_frame = camera.width_resolution / 2

        new_bearing = camera.bearing
        if x_center_pixel > x_center_frame:
            fator = 1 - ((camera.width_resolution - x_center_pixel) / (camera.width_resolution/2))
            diff_degrees = fator * math.degrees(camera.hfov/2)
            new_bearing = new_bearing + diff_degrees
            if new_bearing > 360:
                new_bearing = new_bearing - 360
        else:
            fator = 1- (x_center_pixel / (camera.width_resolution/2))
            diff_degrees = fator * math.degrees(camera.hfov/2)
            new_bearing = new_bearing - diff_degrees
            if new_bearing < 0:
                new_bearing = 360 - abs(new_bearing)

        new_distance = ((real_height * camera.focal_length_px) / pixel_height)
        new_distance = (new_distance / 1000)  # mm to m
        distance_from_camera = new_distance
        new_position_lat, new_position_lon = Converter.polar_to_geo(camera.lat, camera.lon, new_bearing, distance_from_camera)
        new_position_x, new_position_y = Converter.geo_to_xy(new_position_lat, new_position_lon)
        return new_position_x,new_position_y, new_bearing, distance_from_camera