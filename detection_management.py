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
import cv2
import filters

class DetectionManagement(Thread):

    def __init__(self, detector_model, detector_config, classifier_model, location, language):
        Thread.__init__(self)
        self.timestamp_detection = datetime.now()
        self.timestamp_classification = datetime.now()
        self.categories = {}
        self.tracks_list = {}
        self.pixel_inc_width = 80
        self.pixel_inc_height = 80
        self.control_access_track_list = Semaphore(1)
        json_file = open('config/' + location + '.json')
        config_data = json.load(json_file)
        camera_data = config_data['camera']
        calibration_data = config_data['calibration']
        self.calibration = Calibration(calibration_data)
        kinematic.Kinematic.update_noise_function(self.calibration.detection_interval)
        self.load_categories(language)
        self.net_detector = cv2.dnn_DetectionModel(detector_model, detector_config)
        self.net_detector.setInputSize(320, 320)
        self.net_detector.setInputScale(1.0 / 127.5)
        self.net_detector.setInputMean((127.5, 127.5, 127.5))
        self.net_detector.setInputSwapRB(True)
        self.net_classifier = cv2.dnn.readNetFromTensorflow(classifier_model)
        count = cv2.cuda.getCudaEnabledDeviceCount()
        print('Number of GPUs: ' + str(count))
        if count > 0:
            print('CUDA ENABLED')
            self.net_detector.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net_detector.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            self.net_classifier.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net_classifier.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        self.camera = Camera(camera_data, self.calibration)
        self.frame_width = self.camera.resolution_width
        self.frame_height = self.camera.resolution_height

    def load_categories(self, language):
        json_file = open('classifier/ship_types_' + language + '.json')
        config_data = json.load(json_file)

        data = config_data['cargo']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

        data = config_data['military']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

        data = config_data['carrier']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

        data = config_data['cruise']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

        data = config_data['tanker']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

        data = config_data['unknown']
        category = Category(data['id'], data['description'], data['avg_height'])
        self.categories[category.id] = category

    def detect_estimate_and_classify(self):
        raw_img = self.camera.next_frame()
        if raw_img is not None:
            # img_for_detection = cv2.convertScaleAbs(raw_img, alpha=self.calibration.alpha, beta=self.calibration.beta)
            now = datetime.now()
            elapsed_time = now - self.timestamp_detection
            if elapsed_time.seconds >= Kinematic.dt:
                detections = self.detect(raw_img)
                self.timestamp_detection = datetime.now()
                self.classify(raw_img, detections)
            return raw_img, self.tracks_list
        return None, None

    def detect(self, img_for_detection):
        detections = []
        classIds, confs, bbox = self.net_detector.detect(img_for_detection,
                                                         confThreshold=self.calibration.threshold_detection)
        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                if classId == 9 and confidence > self.calibration.threshold_detection_vessel:
                    detections.append([confidence, box])
        return detections

    def classify(self, raw_img, detections):
        for detection in detections:
            detection_confidence = detection[0]
            x = detection[1][0]
            y = detection[1][1]
            w = detection[1][2]
            h = detection[1][3]

            x = x - int(self.pixel_inc_width / 2)
            y = y - int(self.pixel_inc_height / 2)
            size_w = w + self.pixel_inc_width
            size_h = h + self.pixel_inc_height

            if x < 0:
                x = 0
            if y < 0:
                y = 0

            vessel_img = raw_img[y:y + size_h, x:x + size_w]
            vessel_img, w, h = filters.transform(vessel_img, size_w, size_h)
            new_img = cv2.normalize(vessel_img, None, self.calibration.alpha, self.calibration.beta, cv2.NORM_MINMAX,dtype=cv2.CV_32F)

            predictions = None
            now = datetime.now()
            elapsed_time = now - self.timestamp_classification
            if elapsed_time.seconds >= self.calibration.classification_interval:
                detections = self.detect(raw_img)
                self.timestamp_classification = datetime.now()
                self.classify(raw_img, detections)
                self.net_classifier.setInput(cv2.dnn.blobFromImage(new_img, size=(filters.crop_max, filters.crop_max), swapRB=True, crop=False))
                predictions = self.net_classifier.forward()

            self.update(detection_confidence, predictions, [x, y, size_w, size_h])

    def update(self, detection_confidence, predictions, detected_bbox):
        max_value = None
        max_index = None
        if predictions is not None:
            max_index = 0
            max_value = predictions[0][0]
            for i in range(len(predictions[0])):
                if max_value < predictions[0][i]:
                    max_index = i
                    max_value = predictions[0][i]
            if max_value < self.calibration.threshold_classification_vessel:
                max_index = 5
                max_value = 1
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
                        if track_existent.classification.detection_confidence < track.classification.detection_confidence:
                            track_existent = track
            if track_existent is None:
                track_existent = Track(self.categories[5])

            if max_value is not None:
                track_existent.classification.update(detection_confidence, max_value, self.categories, max_index)
            track_existent.kinematic.update(detected_bbox, self.frame_width, self.frame_height, self.camera,
                                            self.calibration, track_existent.classification.category.avg_height)

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
                if k_diff.seconds > 5 * Kinematic.dt and c_diff.seconds > 5 * Kinematic.dt:
                    track.kinematic.lost = True
                if k_diff.seconds > 10 * Kinematic.dt and c_diff.seconds > 10 * Kinematic.dt:
                    tracks_to_remove.append(track)

            with self.control_access_track_list:
                for track in tracks_to_remove:
                    # print("Removed track:" + track.uuid)
                    del self.tracks_list[track.uuid]
            time.sleep(10)
