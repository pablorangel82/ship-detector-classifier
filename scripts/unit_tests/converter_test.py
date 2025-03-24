from core.converter import Converter

def polar_to_xy(bearing, distance):
    x, y  = Converter.polar_to_xy(0,0,bearing,distance)
    print(f'\nBearing: {bearing} and Distance: {distance}')
    print(f'\nx: {x} , y: {y}')
    print('\n')


def xy_to_polar(x, y):
    bearing, distance = Converter.xy_to_polar(0,0,x,y)
    print(f'\nx: {x} , y: {y}')
    print(f'\nBearing: {bearing} and Distance: {distance}')
    print('\n')

def test_xy_to_polar():
    print('Testing converstion methods from xy to polar...')
    xy_to_polar(0,0) 
    xy_to_polar(0,10) 
    xy_to_polar(10,10) 
    xy_to_polar(10,0) 
    xy_to_polar(10,-10)
    xy_to_polar(0,-10) 
    xy_to_polar(-10,-10)
    xy_to_polar(-10,0) 
    xy_to_polar(-10,10) 

def test_polar_to_xy():
    print('Testing converstion methods from polar to xy...')
    polar_to_xy(0,0) 
    polar_to_xy(0,10) 
    polar_to_xy(45,10) 
    polar_to_xy(90,10) 
    polar_to_xy(135,10) 
    polar_to_xy(180,10) 
    polar_to_xy(225,10) 
    polar_to_xy(270,10) 
    polar_to_xy(315,10)