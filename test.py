from camera import Camera
from track import Track

# camera = Camera(-22.90981058690016, -43.159550877242054,[0,0,0])
# track = Track(1, -22.89750771788674, -43.15667996000589, 0, 0, 'Desconhecido', [0,0,0,0])
# bearing, distance = camera.geo_to_polar_coordinate(track.lat, track.lon)
# track.distance = distance
# track.bearing = bearing
# print(track.bearing, track.distance)

camera1 = Camera(None,None,[0,0,0])

print(camera1.xy_to_polar_coordinate([1000,1000]))
print(camera1.xy_to_polar_coordinate([1000,-1000]))
print(camera1.xy_to_polar_coordinate([-1000,-1000]))
print(camera1.xy_to_polar_coordinate([-1000,1000]))



