import copy
import cv2
import json
from datetime import datetime
import time
import torch
from ultralytics import YOLO
import os
from threading import Thread, Semaphore
from core.category import Category
from core.calibration import Calibration
from core.camera import Camera
from core.tmm import Track
from core.category import Category
import logging

class DCM(Thread):
    def __init__(self, config_path, language):
        Thread.__init__(self)
        self.tracks_list = {}
        self.control_access_track_list = Semaphore(1)
        json_file = open(config_path+'.json')
        config_data = json.load(json_file)
        camera_data = config_data['camera']
        calibration_data = config_data['calibration']
        self.calibration = Calibration(calibration_data)
        Category.load_categories(language)
        count = torch.cuda.device_count()
        logging.info('\n### Model Setup ###')
        logging.info(f'* Config file: {config_path+'.json'}')
        logging.info(f'* Number of GPUs: {str(count)}')
        self.devices = 'cpu'
        if torch.cuda.is_available():
            self.devices = []
            for i in range (count):
                self.devices.append(i)
            logging.info(f'* CUDA ENABLED. Devices: {self.devices}')
        else:
            logging.info(f'* CUDA not enabled. You may experience reduced performance.')
        model_path = os.path.join('core/models/',"model.pt")
        logging.info(f'* Model path: {str(model_path)}')
        self.net_classifier = YOLO(model_path)
        self.net_classifier.conf = self.calibration.threshold_confidence
        self.net_classifier.iou = self.calibration.threshold_iou_detection
        self.net_classifier.mode = 'track'
        self.net_classifier.agnostic = True  
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
        img_width = self.calibration.train_image_width
        img_height = self.calibration.train_image_height
        img = cv2.resize(raw_img, (img_width, img_height), cv2.INTER_LINEAR)
        detection_results = self.net_classifier.predict([img],verbose=False,imgsz=img_width,device = self.devices,conf=self.calibration.threshold_confidence, iou=self.calibration.threshold_iou_detection)
        
        for result in detection_results:
            for box in result.boxes:
                confidence = max(box.conf.tolist())
                index_confidence = box.conf.tolist().index (confidence)
                label = box.cls.tolist()[index_confidence]
                bounding_box = box.xyxy[0]
                x = int((bounding_box[0] * self.frame_width) / img_width)
                y = int((bounding_box[1] * self.frame_height) / img_height)
                width = int((bounding_box[2]* self.frame_width) / img_width) - x
                height = int((bounding_box[3] * self.frame_height) / img_height) - y 
                bbox = [x, y, width, height]
                self.tracking(confidence, label, bbox)

    def tracking(self, confidence, label, detected_bbox):
        track_candidate = None
        best_iou = None
        iou=None
        with self.control_access_track_list:
            for track in self.tracks_list.values():
                iou = track.calculate_iou(detected_bbox)
                if iou >= self.calibration.threshold_iou_tracking:
                    if best_iou is None or iou > best_iou:
                        track_candidate = track
                        best_iou = iou

            if best_iou is None:
                track_candidate = Track(self.camera.id)
            
            if confidence < self.calibration.threshold_classification:
                confidence = 1
                label = len(Category.CATEGORIES) - 1
                logging.info(f'{confidence} < {self.calibration.threshold_classification}')
            track_candidate.update(detected_bbox,self.camera,confidence, int(label))
            self.tracks_list[track_candidate.uuid] = track_candidate
        return track_candidate

    def run(self):
        while True:
            tracks_to_remove = []
            for track in self.tracks_list.values():
                current_time = datetime.now()
                k_diff = current_time - track.get_timestamp()
                if track.lost is False and k_diff.seconds > 5:
                    track.lost = True
                    continue
                if k_diff.seconds > 10:
                    tracks_to_remove.append(track)

            with self.control_access_track_list:
                for track in tracks_to_remove:
                    del self.tracks_list[track.uuid]
            time.sleep(1)
