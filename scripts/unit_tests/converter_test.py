import unittest
import logging
from core.converter import Converter

logging.basicConfig(level=logging.INFO, format='%(message)s', )

class ConverterTest():

    test_case = unittest.TestCase()

    @staticmethod
    def polar_to_xy(bearing, distance, expected_x, expected_y):
        x, y  = Converter.polar_to_xy(0,0,bearing,distance)
        ConverterTest.test_case.assertAlmostEqual(x,expected_x,2)
        ConverterTest.test_case.assertAlmostEqual(y,expected_y,2) 
        return x,y

    @staticmethod
    def xy_to_polar(x, y, expected_bearing, expected_distance):
        bearing, distance = Converter.xy_to_polar(0,0,x,y)
        ConverterTest.test_case.assertAlmostEqual(bearing,expected_bearing,2)
        ConverterTest.test_case.assertAlmostEqual(distance,expected_distance,2) 
        return bearing,distance
    
    @staticmethod
    def test_xy_to_polar():
        logging.info('Testing convertion methods from xy to polar...')       
        ConverterTest.xy_to_polar(0,0,0,0) 
        ConverterTest.xy_to_polar(0,10,0,10) 
        ConverterTest.xy_to_polar(10,5,63.43,11.18)
        ConverterTest.xy_to_polar(10,10,45,14.14) 
        ConverterTest.xy_to_polar(10,0, 90, 10) 
        ConverterTest.xy_to_polar(10,-10, 135, 14.14)
        ConverterTest.xy_to_polar(0,-10, 180, 10) 
        ConverterTest.xy_to_polar(-10,-10, 225, 14.14)
        ConverterTest.xy_to_polar(-10,0, 270, 10) 
        ConverterTest.xy_to_polar(-10,10, 315, 14.14) 

    @staticmethod
    def test_polar_to_xy():
        logging.info('Testing convertion methods from polar to xy...')
        ConverterTest.polar_to_xy(0,0,0,0) 
        ConverterTest.polar_to_xy(0,10,0,10) 
        ConverterTest.polar_to_xy(45,10,7.07,7.07) 
        ConverterTest.polar_to_xy(90,10, 10, 0) 
        ConverterTest.polar_to_xy(135,10, 7.07, -7.07) 
        ConverterTest.polar_to_xy(180,10,0,-10) 
        ConverterTest.polar_to_xy(225,10,-7.07,-7.07) 
        ConverterTest.polar_to_xy(270,10, -10,0) 
        ConverterTest.polar_to_xy(315,10,-7.07,7.07)