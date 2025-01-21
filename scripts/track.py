import math
import uuid
import classification
import kinematic
import category


class Track:
    def __init__(self):
        self.uuid = 'UUID-EN-CAMERA-' + str(uuid.uuid4())
        self.kinematic = kinematic.Kinematic()
        self.classification = classification.Classification()
        self.name = None
        

    def to_string(self):
        string = '\nId: ' + self.get_name() + '\n Classification: ' + self.classification.to_string() + '\n Kinematic: ' + self.kinematic.to_string()
        return string

    def get_name(self):
        name = self.name
        if name is None:
             name = '?'
        return name

    def to_json(self):
        name = ''
        if self.get_name() is not None:
            name = self.get_name()
        classification = self.classification.to_string()
        lost = 'false'
        if self.kinematic.lost:
            lost = 'true'
        lat, lon, speed, course, bearing, dist, bbox = self.kinematic.get_current_kinematic()
        if lat and lon is not None:
            distance_realibility = 'false'
            unknown_id = (category.Category.CATEGORIES[len(category.Category.CATEGORIES) -1]).id
            if self.classification.category.id != unknown_id and speed is not None:
                distance_realibility = 'true'
                speed = float(speed)
                course =float(course)
                dist = round(self.kinematic.distance_from_camera / 1852, 2)
            else:
                speed = None
                course = None
                dist = None
            
            obj = {
                "name" : self.get_name(),
                "lat" : lat,
                "lon": lon,
                "distance_from_camera" : dist,
                "px": float(bbox[0]),
                "py": float(bbox[1]),
                "width": float(bbox[2]),
                "height": float(bbox[3]),
                "speed": speed,
                "course": course,
                "bearing": bearing,
                "lost": lost,
                "classification": classification,
                "distance_realibility":distance_realibility
            }
        return obj