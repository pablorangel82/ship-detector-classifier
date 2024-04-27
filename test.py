import json
import math

import kinematic
from GenericList import GenericList
from calibration import Calibration
from camera import Camera
from track import Track

# camera = Camera(-22.90981058690016, -43.159550877242054,[0,0,0])
# track = Track(1, -22.89750771788674, -43.15667996000589, 0, 0, 'Desconhecido', [0,0,0,0])
# bearing, distance = camera.geo_to_polar_coordinate(track.lat, track.lon)
# track.distance = distance
# track.bearing = bearing
# print(track.bearing, track.distance)

# camera1 = Camera(None,None,[0,0,0])
#
print(kinematic.Kinematic.polar_to_xy(1000, 1000, 90, 100))
# bearing, distance = kinematic.Kinematic.xy_to_polar(0,0, 1200 - (1920/2) ,1080)
# print(bearing, distance)
# bearing, distance = kinematic.Kinematic.geo_to_polar(-22.912759833, -43.1582615, -22.89750771788674, -43.15667996000589)
# print(bearing, distance)