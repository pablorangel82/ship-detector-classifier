from core.kinematic import Kinematic

class GroundTruth:
    def __init__(self, lat, lng, course, speed, bearing, azimuth, physical_zoom):
        self.lat = lat
        self.lng = lng
        self.course = course
        self.speed = speed
        self.bearing = bearing
        self.azimuth = azimuth
        self.physical_zoom = physical_zoom
        self.x,self.y = Kinematic.geo_to_xy(lat,lng)
        self.vx,self.vy = Kinematic.polar_to_xy(None,None,course,speed)

    def estimate (self, delta_t):
        x = self.x + (self.speed * delta_t)
        y = self.y + (self.speed * delta_t)
        self.lat,self.lng = Kinematic.xy_to_geo(x,y)
        self.x,self.y = Kinematic.geo_to_xy(self.lat,self.lng)
        self.bearing +=0.002
        self.vx, self.vy = Kinematic.polar_to_xy(None,None,self.course,self.speed)