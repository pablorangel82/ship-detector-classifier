from core.camera import Camera
from core.converter import Converter
import math
import unittest

class CameraTest:
    test_case = unittest.TestCase()
    camera_data = {}
    camera_data['id'] = "Unit Test"
    camera_data['address'] = None
    camera_data['latitude'] = -22.912246879883874
    camera_data['longitude'] = -43.15833890364963
    camera_data['reference_azimuth'] = 336
    camera_data['reference_elevation'] = 0
    camera_data['installation_height'] = 16.4
    camera_data['surveillance_radius'] = 3000
    camera_data['focus_frame_view'] = 350
    camera_data['hfov_min'] = 2.1
    camera_data['hfov_max'] = 63.7
    camera_data['zoom_multiplier_min'] = 0
    camera_data['zoom_multiplier_max'] = 30
    camera_data['zoom_lens_min'] = 4.3
    camera_data['zoom_lens_max'] = 129
    camera_data['height_resolution'] = 1080
    camera_data['width_resolution'] = 1920
    camera_data['sensor_width']= 5.6
    camera_data['sensor_height']= 3.1
    camera_data['frame_rate'] = 30
    camera = Camera(camera_data)

    def test_focal_lengh_calculation(real_height, bbox): 
        CameraTest.camera.set_to_track_position(60, 3200)
        x, y, b, d = CameraTest.camera.monocular_vision_detection_method_2(real_height, bbox)
        new_position_lat, new_position_lon = Converter.xy_to_geo(x,y)
        
    @staticmethod
    def test_pan():
        CameraTest.camera.ref_azimuth = 0
        CameraTest.test_case.assertAlmostEqual(CameraTest.camera.estimate_pan(0), 0.0, places=2)
        CameraTest.test_case.assertAlmostEqual(CameraTest.camera.estimate_pan(90), 0.5, places=2)
        CameraTest.test_case.assertAlmostEqual(CameraTest.camera.estimate_pan(180), 1.0, places=2)
        CameraTest.test_case.assertAlmostEqual(CameraTest.camera.estimate_pan(270), -0.5, places=2)
        CameraTest.test_case.assertAlmostEqual(CameraTest.camera.estimate_pan(360), 0.0, places=2)
        CameraTest.camera.ref_azimuth = 30
        CameraTest.test_case.assertAlmostEqual(round(CameraTest.camera.estimate_pan(0),2), -0.17, places=3)
        CameraTest.camera.ref_azimuth = 90
        CameraTest.test_case.assertAlmostEqual(CameraTest.camera.estimate_pan(90), 0, places=2)
        CameraTest.camera.ref_azimuth = 270
        CameraTest.test_case.assertAlmostEqual(CameraTest.camera.estimate_pan(180), -0.5, places=2)
        CameraTest.camera.ref_azimuth = 20
        CameraTest.test_case.assertAlmostEqual(round(CameraTest.camera.estimate_pan(350),2), -0.17, places=2)
   
    @staticmethod
    def test_tilt():
        CameraTest.camera.ref_elevation = 0
        CameraTest.camera.installation_height = 10
        CameraTest.test_case.assertAlmostEqual(CameraTest.camera.estimate_tilt(0), -1, places=2)
        CameraTest.test_case.assertAlmostEqual(CameraTest.camera.estimate_tilt(10), -0.5, places=2)
        CameraTest.test_case.assertAlmostEqual(CameraTest.camera.estimate_tilt(90), -0.07044657495455442, places=2)
        CameraTest.camera.installation_height = 1
        CameraTest.test_case.assertAlmostEqual(CameraTest.camera.estimate_tilt(1000000000000), 0, places=2)

    @staticmethod
    def test_zoom_estimation():
        
        CameraTest.camera.ref_elevation = -3.2
        CameraTest.camera.installation_height = 30
        CameraTest.camera.focus_frame_view = 350
        CameraTest.camera.reference_azimuth = 338.5
        print(CameraTest.camera.estimate_zoom_factor_by_focal_estimation(1360))