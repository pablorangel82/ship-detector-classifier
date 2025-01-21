import copy
import cv2
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
import os

class DetectionManagement(Thread):

    def __init__(self, source, language):
        Thread.__init__(self)
        self.timestamp_detection = datetime.now()
        self.timestamp_classification = datetime.now()
        self.tracks_list = {}
        Kinematic.update_noise_function()
        self.control_access_track_list = Semaphore(1)
        resources_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources/")
        source_path = os.path.join(resources_path,source+".json")
        json_file = open(source_path)
        config_data = json.load(json_file)
        camera_data = config_data['camera']
        calibration_data = config_data['calibration']
        self.calibration = Calibration(calibration_data)
        Category.load_categories(language)
        count = torch.cuda.device_count()
        print('Number of GPUs: ' + str(count))
        device = 'cpu'
        if torch.cuda.is_available():
            print('CUDA ENABLED')
            device = 'cuda:0'
        model_path = os.path.join(resources_path,"best.pt")
        self.net_classifier = YOLO(model_path).to(device)
        self.net_classifier.conf = self.calibration.threshold_confidence
        self.net_classifier.iou = self.calibration.threshold_intersection
        self.net_classifier.mode = 'track'
        self.net_classifier.agnostic = False  
        self.net_classifier.multi_label = False
        self.camera = Camera(camera_data)

    def detect_estimate_and_classify(self):
        raw_img = self.camera.next_frame()
        if raw_img is not None:
            self.timestamp_detection = datetime.now()
            self.detect_and_classify(raw_img)
            with self.control_access_track_list:
                return copy.deepcopy(raw_img), copy.deepcopy(self.tracks_list)
        return None, None

    def detect_and_classify(self, raw_img):
        self.frame_height, self.frame_width, channels = raw_img.shape
        if self.calibration.resize == "True":
            img_width = self.calibration.train_image_width
            img_height = self.calibration.train_image_height
            img = cv2.resize(raw_img, (img_width, img_height), cv2.INTER_AREA)
        else:
            img = raw_img
            img_width = self.frame_width
            img_height = self.frame_height
        detection_results = self.net_classifier.predict([img],verbose=False,conf=self.calibration.threshold_confidence, iou=self.calibration.threshold_intersection)
        
        for result in detection_results:
            for box in result.boxes:
                name = max(box.cls.tolist())
                confidence = max(box.conf.tolist())
                bounding_box = box.xyxy[0]
                x = int((bounding_box[0] * self.frame_width) / img_width)
                y = int((bounding_box[1] * self.frame_height) / img_height)
                width = int((bounding_box[2]* self.frame_width) / img_width) - x
                height = int((bounding_box[3] * self.frame_height) / img_height) - y 
                bbox = [x, y, width, height]
                self.estimate(confidence, name, bbox)

    def bounding_intersection(self, point, rect):
        res_x = point [0] >= rect [0] and point [0] <= rect [1]
        res_y = point [1] >= rect [2] and point [1] <= rect [3]
        return res_x and res_y

    def estimate(self, confidence, label, detected_bbox):
        track_existent = None
        with self.control_access_track_list:
            for track in self.tracks_list.values():
                old_bbox = track.kinematic.pixel_positions.get_current_value()
                old_x1 = old_bbox[0]
                old_y1 = old_bbox[1]
                old_x2 = old_bbox[0] + int(old_bbox[2])
                old_y2 = old_bbox[1] + int(old_bbox[3])
                
                new_x1 = detected_bbox[0]
                new_y1 = detected_bbox[1]
                new_x2 = detected_bbox[0] + int(detected_bbox[2])
                new_y2 = detected_bbox[1] + int(detected_bbox[3])
                
                bb1 = [old_x1, old_x2, old_y1, old_y2]
                bb1_up_left_corner = [old_x1, old_y1]
                bb1_up_right_corner = [old_x2, old_y1]
                bb1_down_left_corner = [old_x1, old_y2]
                bb1_down_right_corner = [old_x2, old_y2]
                bb1_center = [int((old_x1+old_x2)/2),int((old_y1+old_y2)/2)]

                bb2 = [new_x1, new_x2, new_y1, new_y2]
                bb2_up_left_corner = [new_x1, new_y1]
                bb2_up_right_corner = [new_x2, new_y1]
                bb2_down_left_corner = [new_x1, new_y2]
                bb2_down_right_corner = [new_x2, new_y2]
                bb2_center = [int((new_x1+new_x2)/2),int((new_y1+new_y2)/2)]

                
                res_bb1_up_left_corner = self.bounding_intersection(bb1_up_left_corner, bb2)
                res_bb1_up_right_corner = self.bounding_intersection(bb1_up_right_corner, bb2)
                res_bb1_down_left_corner = self.bounding_intersection(bb1_down_left_corner, bb2)
                res_bb1_down_right_corner = self.bounding_intersection(bb1_down_right_corner, bb2)
                res_bb1_center = self.bounding_intersection(bb1_center, bb2)

                res_bb2_up_left_corner = self.bounding_intersection(bb2_up_left_corner, bb1)
                res_bb2_up_right_corner = self.bounding_intersection(bb2_up_right_corner, bb1)
                res_bb2_down_left_corner = self.bounding_intersection(bb2_down_left_corner, bb1)
                res_bb2_down_right_corner = self.bounding_intersection(bb2_down_right_corner, bb1)
                res_bb2_center = self.bounding_intersection(bb2_center, bb1)

                is_same_bb1 = res_bb1_center or res_bb1_up_left_corner or res_bb1_up_right_corner or res_bb1_down_left_corner or res_bb1_down_right_corner
                is_same_bb2 = res_bb2_center or res_bb2_up_left_corner or res_bb2_up_right_corner or res_bb2_down_left_corner or res_bb2_down_right_corner

                is_same = is_same_bb1 or is_same_bb2

                if is_same:
                    if track_existent is None:
                        track_existent = track
                    else:
                        if track_existent.classification.confidence < track.classification.confidence:
                            track_existent = track
                    
            if track_existent is None:
                track_existent = Track()
            if confidence < self.calibration.threshold_classification:
                confidence = 1
                label = len(Category.CATEGORIES) - 1
            track_existent.classification.update(confidence, int(label))
            track_existent.kinematic.update(detected_bbox, self.camera,track_existent.classification.category.avg_height)
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
                    del self.tracks_list[track.uuid]
            time.sleep(1)
