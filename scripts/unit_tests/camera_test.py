from core.camera import Camera
from core.converter import Converter
from core.monocular_vision import MonocularVision
import math

camera_data = {}
camera_data['id'] = "Unit Test"
camera_data['address'] = None
camera_data['latitude'] = -22.912246879883874
camera_data['longitude'] = -43.15833890364963
camera_data['reference_azimuth'] = 336
camera_data['reference_altitude'] = 3
camera_data['installation_height'] = 16.4
camera_data['surveillance_radius'] = 3000

camera_data['zoom_x_min'] = 0
camera_data['zoom_x_max'] = 30
camera_data['zoom_lens_min'] = 4.3
camera_data['zoom_lens_max'] = 129
camera_data['height_resolution'] = 1080
camera_data['width_resolution'] = 1920
camera_data['width_sensor']= 6.4
camera_data['height_sensor']= 4.8
                          

camera_data['hfov_max'] = 63.7
camera_data['hfov_min'] = 2.1
camera_data['tilt_range'] = 180
camera_data['pan_range'] = 360
camera_data['frame_rate'] = 30
camera = Camera(camera_data)

 #new_distance = ((14000 * ) / pixel_height)

def calculate_iou(bb1, bb2):
    x1_min, y1_min, x1_max, y1_max = bb1
    x2_min, y2_min, x2_max, y2_max = bb2

    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)

    inter_width = max(0, inter_x_max - inter_x_min)
    inter_height = max(0, inter_y_max - inter_y_min)

    inter_area = inter_width * inter_height

    bb1_area = (x1_max - x1_min) * (y1_max - y1_min)
    bb2_area = (x2_max - x2_min) * (y2_max - y2_min)

    union_area = bb1_area + bb2_area - inter_area

    iou = inter_area / union_area if union_area > 0 else 0
    return iou

def test_focal_lengh_calculation(real_height, bbox): 
    camera.set_to_track_position(6.274725694444444, 0, 30)
    x, y, b, d = MonocularVision.monocular_vision_detection_method_2(camera, real_height, bbox)
    new_position_lat, new_position_lon = Converter.xy_to_geo(x,y)
    print('Pan: ' + str(camera.pan))
    print('Zoom: ' + str(camera.zoom))
    print('Focal (mm): ' + str(camera.focal_length_mm))
    print('Focal (px): ' + str(camera.focal_length_px))
    print('HFOV: ' + str(math.degrees(camera.hfov)))
    print('Dist: ' + str(d))
    print('Bearing: ' + str(b))
    print(new_position_lat,new_position_lon)

    #2945.9633125276887
    #6.274725694444444

def test_polar_to_ptz():
    camera.interval_measured = 1
    camera.tracking()
    print('B: ' + str(camera.bearing))
    print('PZ: ' + str(camera.zoom_multiplier))
    print('P: ' + str(camera.pan))
    print('T: ' + str(camera.tilt))
    print('Z: ' + str(camera.zoom))
    