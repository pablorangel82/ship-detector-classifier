from core.converter import Converter
from datetime import datetime

class GroundTruth:
    def __init__(self, lat, lng, course, speed, timestamp, pan, tilt, zoom):
        self.delta_t = 0
        self.estimated = False
        self.lat = lat
        self.lng = lng
        self.course = course
        self.speed = speed
        self.pan = pan
        self.tilt = tilt
        self.zoom = zoom
        self.timestamp = datetime.fromisoformat(timestamp)
        self.x,self.y = Converter.geo_to_xy(lat,lng)
        self.vx,self.vy = Converter.polar_to_xy(None,None,course,speed)

    def __str__(self):
        str = f'\n Position {self.lat} {self.lng}'
        str += f'\n Velocity: {self.speed} {self.course}'
        str += f'\n {self.estimated}'
        return str