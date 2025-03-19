from core.converter import Converter

class GroundTruth:
    def __init__(self, category, lat, lng, course, speed, pan, tilt, zoom):
        self.category = category
        self.lat = lat
        self.lng = lng
        self.course = course
        self.speed = speed
        self.pan = pan
        self.tilt = tilt
        self.zoom = zoom
        self.x,self.y = Converter.geo_to_xy(lat,lng)
        self.vx,self.vy = Converter.polar_to_xy(None,None,course,speed)

    def estimate (self, delta_t):
        x = self.x + (self.speed * delta_t)
        y = self.y + (self.speed * delta_t)
        self.lat,self.lng = Converter.xy_to_geo(x,y)
        self.x,self.y = Converter.geo_to_xy(self.lat,self.lng)
        self.bearing +=0.002
        self.vx, self.vy = Converter.polar_to_xy(None,None,self.course,self.speed)