from camera import Camera
from kinematic import Kinematic

camera_data = {}
camera_data['address'] = None
camera_data['latitude'] = -22.912759833
camera_data['longitude'] = -43.1582615
camera_data['standard_bearing'] = 336
zoom_min = camera_data['zoom_min'] = 0
zoom_max = camera_data['zoom_max'] = 30
height_resolution = camera_data['height_resolution'] = 1080
width_resolution = camera_data['width_resolution'] = 1920
camera_data['hfov_max'] = 63.7
camera_data['hfov_min'] = 2.1
camera_data['tilt_range'] = 350
camera_data['pan_range'] = 360
camera_data['frame_rate'] = 30

camera = Camera(camera_data)
camera.set_to_track_position(6.274725694444444, 0, 27.5)
print(camera.pan)
print(camera.zoom)
print(camera.focal_length)
new_distance = ((14354.24 * camera.focal_length) / 129)
new_distance = (new_distance / 1000)  # mm to m

print(new_distance)
new_position_lat, new_position_lon = Kinematic.polar_to_geo(camera.lat, camera.lon, 6, new_distance)
print(new_position_lat,new_position_lon)

#2945.9633125276887
#6.274725694444444