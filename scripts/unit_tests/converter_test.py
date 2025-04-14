import unittest
import logging
from core.converter import Converter

logging.basicConfig(level=logging.INFO, format='%(message)s', )

class ConverterTest():

    test_case = unittest.TestCase()

    @staticmethod
    def polar_to_xy(ref_x, ref_y, bearing, distance, expected_x, expected_y):
        x, y  = Converter.polar_to_xy(ref_x, ref_y, bearing,distance)
        ConverterTest.test_case.assertAlmostEqual(x,expected_x,2)
        ConverterTest.test_case.assertAlmostEqual(y,expected_y,2) 
        return x,y

    @staticmethod
    def xy_to_polar(ref_x, ref_y, x, y, expected_bearing, expected_distance):
        bearing, distance = Converter.xy_to_polar(ref_x, ref_y, x, y)
        ConverterTest.test_case.assertAlmostEqual(bearing,expected_bearing,2)
        ConverterTest.test_case.assertAlmostEqual(distance,expected_distance,2) 
        return bearing,distance
    
    def cases_polar_to_xy(self):
        ConverterTest.polar_to_xy(0, 0, 0.0, 10.0, expected_x=0.0, expected_y=10.0)
        ConverterTest.polar_to_xy(0, 0, 90.0, 10.0, expected_x=10.0, expected_y=0.0)
        ConverterTest.polar_to_xy(0, 0, 180.0, 10.0, expected_x=0.0, expected_y=-10.0)
        ConverterTest.polar_to_xy(0, 0, 270.0, 10.0, expected_x=-10.0, expected_y=0.0)
        ConverterTest.polar_to_xy(0, 0, 45.0, 10.0, expected_x=7.07, expected_y=7.07)
        ConverterTest.polar_to_xy(0, 0, 315.0, 10.0, expected_x=-7.07, expected_y=7.07)
        ConverterTest.polar_to_xy(0, 0, 135.0, 10.0, expected_x=7.07, expected_y=-7.07)
        ConverterTest.polar_to_xy(0, 0, 225.0, 10.0, expected_x=-7.07, expected_y=-7.07)
        ConverterTest.polar_to_xy(100, 50, 60.0, 20.0, expected_x=117.32, expected_y=60.0)
        ConverterTest.polar_to_xy(0, 0, 30.0, 1.0, expected_x=0.5, expected_y=0.87)
        ConverterTest.polar_to_xy(0, 0, 120.0, 1000.0, expected_x=866.03, expected_y=-500.0)
        ConverterTest.polar_to_xy(None, None, 0.0, 10.0, expected_x=0.0, expected_y=10.0)
        ConverterTest.polar_to_xy(None, None, 90.0, 10.0, expected_x=10.0, expected_y=0.0)
        ConverterTest.polar_to_xy(None, None, 210.0, 5.0, expected_x=-2.5, expected_y=-4.33)
        ConverterTest.polar_to_xy(None, None, 0.0, 0.0, expected_x=0.0, expected_y=0.0)
        ConverterTest.polar_to_xy(None, None, 73.2, 15.0, expected_x=14.359, expected_y=4.335)
        ConverterTest.polar_to_xy(50, 50, 0.0, 10.0, expected_x=50.0, expected_y=60.0)      
        ConverterTest.polar_to_xy(50, 50, 90.0, 10.0, expected_x=60.0, expected_y=50.0)     
        ConverterTest.polar_to_xy(50, 50, 180.0, 10.0, expected_x=50.0, expected_y=40.0)    
        ConverterTest.polar_to_xy(50, 50, 270.0, 10.0, expected_x=40.0, expected_y=50.0)    
        ConverterTest.polar_to_xy(-20, 30, 45.0, 14.14, expected_x=-10.0, expected_y=40.0)  
        ConverterTest.polar_to_xy(-20, 30, 225.0, 14.14, expected_x=-30.0, expected_y=20.0) 
        ConverterTest.polar_to_xy(-100, -100, 135.0, 14.14, expected_x=-90.0, expected_y=-110.0) 
        ConverterTest.polar_to_xy(-100, -100, 315.0, 14.14, expected_x=-110.0, expected_y=-90.0) 
        ConverterTest.polar_to_xy(70, -50, 120.0, 20.0, expected_x=87.32, expected_y=-60.0)
        ConverterTest.polar_to_xy(70, -50, 300.0, 20.0, expected_x=52.68, expected_y=-40.00)
        ConverterTest.polar_to_xy(10, 10, 73.5, 15.0, expected_x=24.38, expected_y=14.26)
        ConverterTest.polar_to_xy(-30, 60, 200.0, 50.0, expected_x=-47.10, expected_y=13.015)
        ConverterTest.polar_to_xy(100, 100, 180.0, 0.0, expected_x=100.0, expected_y=100.0)
        ConverterTest.polar_to_xy(0, 0, 5.0, 10.0, expected_x=0.87, expected_y=9.96)
        ConverterTest.polar_to_xy(0, 0, 355.0, 10.0, expected_x=-0.87, expected_y=9.96)

    def cases_xy_to_polar(self):
        ConverterTest.xy_to_polar(0, 0, 0, 10, expected_bearing=0.0, expected_distance=10.0)
        ConverterTest.xy_to_polar(0, 0, 10, 0, expected_bearing=90.0, expected_distance=10.0)
        ConverterTest.xy_to_polar(0, 0, 0, -10, expected_bearing=180.0, expected_distance=10.0)
        ConverterTest.xy_to_polar(0, 0, -10, 0, expected_bearing=270.0, expected_distance=10.0)
        ConverterTest.xy_to_polar(0, 0, 10, 10, expected_bearing=45.0, expected_distance=14.14)
        ConverterTest.xy_to_polar(0, 0, 10, -10, expected_bearing=135.0, expected_distance=14.14)
        ConverterTest.xy_to_polar(0, 0, -10, -10, expected_bearing=225.0, expected_distance=14.14)
        ConverterTest.xy_to_polar(0, 0, -10, 10, expected_bearing=315.0, expected_distance=14.14)
        ConverterTest.xy_to_polar(0, 0, 0, 0, expected_bearing=0.0, expected_distance=0.0)
        ConverterTest.xy_to_polar(5, 5, 5, 15, expected_bearing=0.0, expected_distance=10.0)
        ConverterTest.xy_to_polar(3, 3, 3, -7, expected_bearing=180.0, expected_distance=10.0)
        ConverterTest.xy_to_polar(2, 2, 12, 2, expected_bearing=90.0, expected_distance=10.0)
        ConverterTest.xy_to_polar(2, 2, -8, 2, expected_bearing=270.0, expected_distance=10.0)
        ConverterTest.xy_to_polar(-5, -5, -10, -10, expected_bearing=225.0, expected_distance=7.07)
        ConverterTest.xy_to_polar(0, 0, 1, 1, expected_bearing=45.0, expected_distance=1.41)
        ConverterTest.xy_to_polar(None, None, 0, 10, expected_bearing=0.0, expected_distance=10.0)
        ConverterTest.xy_to_polar(None, None, 0, -10, expected_bearing=180.0, expected_distance=10.0)
        ConverterTest.xy_to_polar(None, None, 10, 0, expected_bearing=90.0, expected_distance=10.0)
        ConverterTest.xy_to_polar(None, None, -10, 0, expected_bearing=270.0, expected_distance=10.0)
        ConverterTest.xy_to_polar(None, None, 3, 3, expected_bearing=45.0, expected_distance=4.24)
        ConverterTest.xy_to_polar(None, None, -3, 3, expected_bearing=315.0, expected_distance=4.24)
        ConverterTest.xy_to_polar(None, None, 3, -3, expected_bearing=135.0, expected_distance=4.24)
        ConverterTest.xy_to_polar(None, None, -3, -3, expected_bearing=225.0, expected_distance=4.24)
        ConverterTest.xy_to_polar(None, None, 0, 0, expected_bearing=0.0, expected_distance=0.0)
        ConverterTest.xy_to_polar(None, None, 5, 8, expected_bearing=32.01, expected_distance=9.43)
        ConverterTest.xy_to_polar(None, None, -6, -8, expected_bearing=216.87, expected_distance=10.0)
        ConverterTest.xy_to_polar(None, None, 0.1, 0.1, expected_bearing=45.0, expected_distance=0.14)
        ConverterTest.xy_to_polar(None, None, 1000, 0, expected_bearing=90.0, expected_distance=1000.0)
    