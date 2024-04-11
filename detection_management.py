import math
from datetime import datetime
import time
from threading import Thread

from track import Track


class DetectionManagement(Thread):
    tracks_list = []
    threshold_classifier = 0
    categories = []

    def __init__(self, threshold_classifier, category_file_name):
        Thread.__init__(self)
        self.threshold_classifier = threshold_classifier
        with open(category_file_name, 'rt') as f:
            self.categories = f.read().rstrip('\n').split('\n')

    def update_track(self, preds, bbox):
        category = self.categories[5]
        max_index = 0
        max_value = preds[0][0]
        for i in range(len(preds[0])):
            if max_value < preds[0][i]:
                max_index = i
                max_value = preds[0][i]

        for i in range(len(self.tracks_list)):
            track = self.tracks_list[i]
            old_x = track.bbox[0]
            old_y = track.bbox[1]
            old_width = track.bbox[2]
            old_height = track.bbox[3]
            center_x = bbox[0] + int(bbox[2] / 2)
            center_y = bbox[1] + int(bbox[3] / 2)

            if (old_x + old_width) > center_x > old_x and (old_y + old_height) > center_y > old_y:
                if max_value < self.threshold_classifier:
                    max_index = 5
                    max_value = 1
                track.update(max_value, self.categories, max_index, bbox)

                return track

        track = Track(None, None, None, None, category, bbox, max_value)
        self.tracks_list.append(track)
        return track

    def run(self):
        while True:
            for track in self.tracks_list:
                actual_time = datetime.now()
                diff = actual_time - track.timestamp
                if diff.seconds > 2:
                    self.tracks_list.remove(track)
                    # print("Removed track:"+track.uuid)
            time.sleep(1)
