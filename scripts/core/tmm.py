import uuid
import core.classification
from core.estimation_submodule import Kinematic
from core.monocular_vision_submodule import MonocularVision
from core.converter import Converter
import core.category
import numpy as np

class Track:
    
    def __init__(self, source):
        self.uuid = source + '-' + str(uuid.uuid4())
        self.classification = core.classification.Classification()
        self.name = None
        self.lat = None
        self.lon = None
        self.x =None
        self.y = None
        self.speed = None
        self.course = None
        self.bearing = None
        self.distance_from_camera = None
        self.bbox = None
        self.bbox_to_draw = None
        self.lost = False
        self.bbox_xy = Kinematic (measurement_noise=1, process_noise=0.15, initial_gain=(1000, 1000, 1000, 1000))
        self.bbox_wh = Kinematic (measurement_noise=1, process_noise=0.15, initial_gain=(1000, 1000, 1000, 1000))
        self.utm = Kinematic (measurement_noise=1, process_noise=0.15,initial_gain=(200, 5000, 200, 5000))
        self.vx_vy = Kinematic (measurement_noise=1, process_noise=0.0000013, initial_gain=(5000, 200, 5000, 200))

    def update(self, detected_bbox, camera, confidence, category_index):
        self.lost = False
        px = detected_bbox[0]
        py = detected_bbox[1]
        w = detected_bbox[2]
        h = detected_bbox[3]

        self.bbox_xy.update(px, py)
        self.bbox_wh.update(w,h)
        self.bbox = [self.bbox_xy.position[0], self.bbox_xy.position[1], self.bbox_wh.position[0], self.bbox_wh.position[1]]
        self.bbox_to_draw = [px, self.bbox_xy.position[1], self.bbox_wh.position[0], self.bbox_wh.position[1]]

        self.classification.update(confidence, category_index)
     
        air_draught = self.classification.elected[0].avg_air_draught
        x, y, lat, lon, bearing, distance_from_camera = MonocularVision.monocular_vision_detection_method_2(camera,air_draught, self.bbox)
        self.utm.update(x,y)
        self.vx_vy.update(x,y)
        self.x=self.utm.position[0]
        self.y=self.utm.position[1]
        self.bearing,self.distance_from_camera= Converter.xy_to_polar(camera.x,camera.y,self.x,self.y)
        self.lat,self.lon = Converter.xy_to_geo(self.x,self.y)

        #self.utm.update(bearing,distance_from_camera)
        # x=self.utm.position[0]
        # y=self.utm.position[1]

        # self.x = x + camera.x
        # self.y = y + camera.y

        #self.lat,self.lon = Converter.xy_to_geo(self.x,self.y)
        #self.bearing,self.distance_from_camera= Converter.xy_to_polar(camera.x,camera.y,self.x,self.y)
        self.speed, self.course = Converter.calculate_speed_and_course(self.vx_vy.velocity[0], self.vx_vy.velocity[1])

    def __str__(self):
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
    
    def calculate_iou(self, detected_bbox):
        x1_min = self.bbox[0]
        y1_min = self.bbox[1]
        x1_max = self.bbox[0] + int(self.bbox[2])
        y1_max = self.bbox[1] + int(self.bbox[3])
        
        x2_min = detected_bbox[0]
        y2_min = detected_bbox[1]
        x2_max = detected_bbox[0] + int(detected_bbox[2])
        y2_max = detected_bbox[1] + int(detected_bbox[3])
        
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)

        inter_width = max(0, inter_x_max - inter_x_min)
        inter_height = max(0, inter_y_max - inter_y_min)

        inter_area = inter_width * inter_height

        bb1_area = (x1_max - x1_min) * (y1_max - y1_min)
        bb2_area = (x2_max - x2_min) * (y2_max - y2_min)

        union_area = bb1_area + bb2_area - inter_area

        iou = inter_area / union_area if union_area > 0 else 0
        return iou

    def get_current_kinematic(self):
        if self.utm is None or self.bbox is None or self.lat is None or self.lon is None:
            return None, None, None, None, None, None, None
        return self.lat, self.lon, self.speed, self.course, self.bearing, self.distance_from_camera, self.bbox_to_draw

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
            if self.classification.category.id != unknown_id:
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
    
