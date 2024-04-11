import uuid
from datetime import datetime


class Track:
    uuid = ''
    lat = 0
    lon = 0
    bearing = 0
    distance = 0
    course = 0
    speed = 0
    category = ''
    bbox = []
    timestamp = 0
    confidence = 0
    votes = [0,0,0,0,0,0]

    def __init__(self, lat, lon, course, speed, category, bbox, confidence):
        self.uuid = 'UUID-EN-CAMERA-' + str(uuid.uuid4())
        self.lat = lat
        self.lon = lon
        self.course = course
        self.speed = speed
        self.category = category
        self.bbox = bbox
        self.confidence = confidence
        self.timestamp = datetime.now()
        self.votes = [0, 0, 0, 0, 0, 0]

    def update(self, confidence, categories, category_index, bbox):
        self.votes[category_index] += 1
        most_voted = 0
        for i in range(len(self.votes)):
            if self.votes[i] > self.votes[most_voted]:
                most_voted = i
        print(self.uuid)
        print(self.votes)
        self.category = categories[most_voted]
        if category_index == most_voted:
            if confidence > self.confidence:
                self.confidence = confidence
            print(self.category)
        else:
            self.confidence = confidence

        self.update_bbox(bbox)

    def update_bbox(self, bbox):
        self.bbox = bbox
        self.timestamp = datetime.now()