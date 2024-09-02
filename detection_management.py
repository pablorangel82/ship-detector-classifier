import copy
import filters
import kinematic
from category import Category
import json
from datetime import datetime
import time
from threading import Thread, Semaphore
from calibration import Calibration
from camera import Camera
from kinematic import Kinematic
from track import Track
import torch
from ultralytics import YOLO

class DetectionManagement(Thread):

    def __init__(self, location, language):
        Thread.__init__(self)
        self.timestamp_detection = datetime.now()
        self.timestamp_classification = datetime.now()
        self.categories = {}
        self.tracks_list = {}
        self.control_access_track_list = Semaphore(1)
        json_file = open('config/' + location + '.json')
        config_data = json.load(json_file)
        camera_data = config_data['camera']
        calibration_data = config_data['calibration']
        self.calibration = Calibration(calibration_data)
        kinematic.Kinematic.update_noise_function(self.calibration.detection_interval)
        self.load_categories(language)
        count = torch.cuda.device_count()
        print('Number of GPUs: ' + str(count))
        device = 'cpu'
        if torch.cuda.is_available():
            print('CUDA ENABLED')
            device = 'cuda'

        self.net_classifier = YOLO("classifier/best.pt").to(device)
        self.net_classifier.conf = self.calibration.threshold_detection
        self.net_classifier.iou = 0.6
        self.net_classifier.agnostic = False  # NMS class-agnostic
        self.net_classifier.multi_label = False
        self.camera = Camera(camera_data, self.calibration)

    def load_categories(self, language):
        json_file = open('classifier/ship_types_' + language + '.json')
        config_data = json.load(json_file)

        data = config_data['cargoship']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

        data = config_data['cruise']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

        data = config_data['fishingboat']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

        data = config_data['passengership']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

        data = config_data['sailboat']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

        data = config_data['warship']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

        data = config_data['unknown']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

    def detect_estimate_and_classify(self):
        raw_img = self.camera.next_frame()
        if raw_img is not None:
            now = datetime.now()
            elapsed_time = now - self.timestamp_detection
            if elapsed_time.seconds >= Kinematic.dt:
                self.timestamp_detection = datetime.now()
                self.detect_and_classify(raw_img)
            with self.control_access_track_list:
                return copy.deepcopy(raw_img), copy.deepcopy(self.tracks_list)
        return None, None

    def detect_and_classify(self, raw_img):
        self.frame_height, self.frame_width, channels = raw_img.shape
        detection_results = self.net_classifier.predict([raw_img],verbose=True)

        for result in detection_results:
            detection_count = result.boxes.shape[0]
            for i in range(detection_count):
                cls = int(result.boxes.cls[i].item())
                name = result.names[cls]
                confidence = float(result.boxes.conf[i].item())
                if confidence < self.calibration.threshold_detection:
                    continue
                bounding_box = result.boxes.xyxy[i].tolist()
                x = int(bounding_box[0])
                y = int(bounding_box[1])
                width = int(bounding_box[2] - x)
                height = int(bounding_box[3] - y)
                bbox = [x, y, width, height]
                self.estimate(confidence, cls, bbox)

    def estimate(self, confidence, label, detected_bbox):

        track_existent = None
        with self.control_access_track_list:
            for track in self.tracks_list.values():
                old_x = track.kinematic.get_pixel_coordinates()[0]
                old_y = track.kinematic.get_pixel_coordinates()[1]
                old_width = track.kinematic.get_pixel_coordinates()[2]
                old_height = track.kinematic.get_pixel_coordinates()[3]
                center_x = detected_bbox[0] + int(detected_bbox[2] / 2)
                center_y = detected_bbox[1] + int(detected_bbox[3] / 2)
                is_same = (old_x + old_width) > center_x > old_x and (old_y + old_height) > center_y > old_y

                if is_same:
                    if track_existent is None:
                        track_existent = track
                    else:
                        if track_existent.classification.confidence < track.classification.confidence:
                            track_existent = track
            if track_existent is None:
                track_existent = Track(self.categories[len(self.categories) - 1])
            if confidence < self.calibration.threshold_classification:
                confidence = 1
                label = len(self.categories) - 1
            track_existent.classification.update(confidence, self.categories, int(label))
            track_existent.kinematic.update(detected_bbox, self.frame_width, self.frame_height, self.camera,
                                            track_existent.classification.category.avg_height)

            track_existent.kinematic.current_bbox = detected_bbox
            self.tracks_list[track_existent.uuid] = track_existent
        return track_existent

    def run(self):
        while True:
            tracks_to_remove = []
            for track in self.tracks_list.values():
                actual_time = datetime.now()
                k_diff = actual_time - track.kinematic.timestamp
                c_diff = actual_time - track.classification.timestamp
                if track.kinematic.lost is False and k_diff.seconds > 5 * Kinematic.dt and c_diff.seconds > 5 * Kinematic.dt:
                    track.kinematic.lost = True
                    continue
                if k_diff.seconds > 10 * Kinematic.dt and c_diff.seconds > 10 * Kinematic.dt:
                    tracks_to_remove.append(track)

            with self.control_access_track_list:
                for track in tracks_to_remove:
                    # print("Removed track:" + track.uuid)
                    del self.tracks_list[track.uuid]
            time.sleep(10)
