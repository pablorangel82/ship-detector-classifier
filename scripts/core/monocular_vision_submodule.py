from core.converter import Converter
import math

class MonocularVision:
     
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
    

    @staticmethod
    def monocular_vision_detection_method_2(camera, real_height, detected_bbox):
        pixel_width = detected_bbox[2]
        pixel_height = detected_bbox[3]
        x_center_pixel = detected_bbox[0] + (pixel_width / 2)
        x_center_frame = camera.sensor_width_resolution / 2
        fator = (x_center_pixel - x_center_frame) / (camera.sensor_width_resolution / 2)
        diff_degrees = fator * (camera.hfov / 2)
        new_bearing = (camera.bearing + diff_degrees) % 360
        new_distance = ((real_height * camera.focal_length_px) / pixel_height)
        new_distance = (new_distance / 1000)  # mm to m
        new_position_x, new_position_y = Converter.polar_to_xy(camera.x, camera.y, new_bearing, new_distance)
        lat, lon = Converter.xy_to_geo(new_position_x,new_position_y)
        
        return new_position_x,new_position_y, lat, lon, new_bearing, new_distance

    @staticmethod
    def monocular_vision_detection_method_3(camera, detected_bbox):
        # bearing estimation with arctan relations (more accurate)
        pixel_width = detected_bbox[2]
        x_center_pixel = detected_bbox[0] + (pixel_width / 2)
        dx = x_center_pixel - camera.sensor_width_resolution / 2.0
        angle_offset = math.degrees(math.atan(dx / camera.fx))
        bearing = (camera.bearing + angle_offset) % 360

        # distance estimation with tilt angle from camera (more accurate)
        y_pixel = detected_bbox[1] + detected_bbox[3]
        delta_px = y_pixel - camera.sensor_height_resolution / 2.0
        delta_angle_rad = math.atan(delta_px / camera.fy)
        alpha_rad = math.radians(camera.elevation) + delta_angle_rad
        tan_alpha = math.tan(alpha_rad)
        distance = camera.installation_height / tan_alpha
        
        # position estimation
        x, y = Converter.polar_to_xy(camera.x, camera.y, bearing, distance)
        lat, lon = Converter.xy_to_geo(x, y)
        
        return x, y, lat, lon, bearing, distance