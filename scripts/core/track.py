import uuid
import core.classification
from core.kinematic import Kinematic
from core.monocular_vision import MonocularVision
from core.converter import Converter
import core.category

class Track:
    
    def __init__(self, source):
        self.uuid = source + '-' + str(uuid.uuid4())
        self.classification = core.classification.Classification()
        self.name = None
        self.lat = None
        self.lon = None
        self.speed = None
        self.course = None
        self.bearing = None
        self.distance_from_camera = None
        self.bbox = None
        self.lost = False
        self.bbox_xy = Kinematic (observation_noise=5)
        self.bbox_wh = Kinematic (observation_noise=5)
        self.utm = Kinematic (observation_noise=17)

    def update(self, detected_bbox, camera, confidence, category_index):
        self.lost = False
        px = detected_bbox[0]
        py = detected_bbox[1]
        w = detected_bbox[2]
        h = detected_bbox[3]

        self.bbox_xy.delta_t = camera.interval_measured
        self.bbox_wh.delta_t = camera.interval_measured
        self.utm.delta_t = camera.interval_measured
        self.bbox_xy.update(px, py)
        self.bbox_wh.update(w,h)
        self.bbox = [self.bbox_xy.position[0], self.bbox_xy.position[1], self.bbox_wh.position[0], self.bbox_wh.position[1]]
        
        self.classification.update(confidence, category_index, self.bbox)
        
        air_draught = self.classification.elected[0].max_air_draught
        detected_bbox [2] = self.classification.elected[3][2]
        detected_bbox [3] = self.classification.elected[3][3]
        estimated_x, estimated_y, self.bearing, distance_from_camera = MonocularVision.monocular_vision_detection_method_2(camera, air_draught, detected_bbox)
        self.utm.update(estimated_x, estimated_y)
        self.lat, self.lon = Converter.xy_to_geo(estimated_x, estimated_y)
        x_cam, y_cam = Converter.geo_to_xy(camera.lat, camera.lon)
        self.distance_from_camera = Converter.euclidian_distance(x_cam,y_cam, self.utm.position[0], self.utm.position[1])
        self.speed, self.course = Converter.calculate_speed_and_course(self.utm.velocity[0], self.utm.velocity[1])

    def to_string(self):
        id = self.get_name()
        lat, lon, speed, course, bearing, distance, bbox = self.get_current_kinematic()
        classification = self.classification.to_string()
        string = '\nID: ' + str(id)
        string = string + '\nClassification: ' + str(classification)
        string = string + '\nPOS: ' + str(lat) + ', ' + str(lon)
        string = string + '\nSPD: ' + str(speed)
        string = string + '\nCOG: ' + str(course)
        string = string + '\nBearing: ' + str(bearing) + ' - ' + ' Distance: ' + str(distance)
        string = string + '\nBbox: ' + str(bbox)
        return string

    def get_current_kinematic(self):
        if self.utm is None or self.bbox is None or self.lat is None or self.lon is None:
            return None, None, None, None, None, None, None
        return self.lat, self.lon, self.speed, self.course, self.bearing, self.distance_from_camera, self.bbox

    def get_name(self):
        name = self.name
        if name is None:
             name = '?'
        return name

    def to_json(self):
        name = self.uuid
        if self.get_name() is not None:
            name = self.get_name()
        classification = self.classification.to_string()
        lost = 'false'
        if self.lost:
            lost = 'true'
        lat, lon, speed, course, bearing, dist, bbox = self.get_current_kinematic()
        if lat and lon is not None:
            distance_realibility = 'false'
            unknown_id = (core.category.Category.CATEGORIES[len(core.category.Category.CATEGORIES) -1]).id
            if self.classification.elected != unknown_id:
                distance_realibility = 'true'
                speed = float(speed)
                course =float(course)
                dist = round(self.distance_from_camera / 1852, 2)
            else:
                speed = None
                course = None
                dist = None
            
            obj = {
                "id" : self.uuid,
                "id_category": self.classification.elected[0].id,
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
    
    def get_timestamp(self):
        return self.utm.timestamp