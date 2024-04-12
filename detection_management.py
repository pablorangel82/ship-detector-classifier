import math
from datetime import datetime
import time
from threading import Thread

from camera import Camera
from track import Track


class DetectionManagement(Thread):
    camera = None
    tracks_list = []
    threshold_classifier = 0.7
    categories_names = []
    pixel_inc_width = 80
    pixel_inc_height = 80

    def __init__(self, location, language):
        Thread.__init__(self)
        self.camera = Camera(location)
        self.load_categories(language)

    def load_categories(self, language):
        categories_filename = 'classifier/ship_types-' + language
        with open(categories_filename, 'rt') as f:
            self.categories_names = f.read().rstrip('\n').split('\n')

    def update_track(self, detection_confidence, preds, bbox):
        category = self.categories_names[5]
        max_index = 0
        max_value = preds[0][0]
        pixel_height = bbox[3] - self.pixel_inc_height
        for i in range(len(preds[0])):
            if max_value < preds[0][i]:
                max_index = i
                max_value = preds[0][i]
        track_existent = None
        for i in range(len(self.tracks_list)):
            track = self.tracks_list[i]
            old_x = track.bbox[0]
            old_y = track.bbox[1]
            old_width = track.bbox[2]
            old_height = track.bbox[3]
            center_x = bbox[0] + int(bbox[2] / 2)
            center_y = bbox[1] + int(bbox[3] / 2)

            if (old_x + old_width) > center_x > old_x and (old_y + old_height) > center_y > old_y:
                if track_existent is None:
                    track_existent = track
                else:
                    if track_existent.detection_confidence < track.detection_confidence:
                        track_existent = track

        if max_value < self.threshold_classifier:
            max_index = 5
            max_value = 1
        if track_existent is not None:
            track_existent.update(detection_confidence, max_value, self.categories_names, max_index, bbox, self.camera, pixel_height)
            return track_existent

        track_existent = Track(detection_confidence, max_value, self.categories_names, max_index, bbox, self.camera, pixel_height)
        print('criando novo: ' + track_existent.uuid)
        self.tracks_list.append(track_existent)
        return track_existent

    def run(self):
        while True:
            for track in self.tracks_list:
                actual_time = datetime.now()
                diff = actual_time - track.timestamp
                if diff.seconds > 2:
                    self.tracks_list.remove(track)
                    # print("Removed track:"+track.uuid)
            time.sleep(2)

