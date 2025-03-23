import math
import logging
from ultralytics import YOLO
import logging
from datetime import datetime
import copy
from core.dcm import DCM
from evaluation.ground_truth import GroundTruth
from core.listener import Listener
import os
from core.viewer import view
import cv2

class KEMEvaluation (Listener):
    RESOLUTION = 1
    def __init__(self, category, confusion_matrix, mcc_table, interval):
        self.trajectories = []
        self.ground_truth = []
        self.category = category
        self.confusion_matrix = confusion_matrix
        self.mcc_table = mcc_table
        self.initial_time = None
        self.interval = interval
        self.mse_overall_results = []

    def receive_evt(self, img, track, evt_type):
        self.trajectories.append(track)
        
    def read_ground_truth(self,path):
        file_path = os.path.join(path,'ground_truth.csv')
        with open(file_path, 'r') as file:
            next(file)
            for line in file:
                values = line.split(',')      
                gt = GroundTruth(self.category,values[2], float(values[3]), float(values[4]), float(values[5]), float(values[6]), float(values[7]), float(values[8]))
                self.ground_truth.append(gt)

    def evaluate(self, path, version):
        dcm = DCM(path+'config', str(version), 'en')
        dcm.listener = self
        self.read_ground_truth(path)
        logging.info ('Detection / Classification Task')
        frames = 0
        ellapsed = 0
        while True:
            gt = self.ground_truth[frames]
            dcm.camera.convert_ptz_to_polar(gt.pan,gt.tilt,gt.zoom)
            frames +=1
            img_to_show,tracks_list = dcm.detect_estimate_and_classify()
            if img_to_show is None and tracks_list is None:
                break
            view(img_to_show, tracks_list, dcm.camera)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            ellapsed+=dcm.camera.interval_measured
        estimated_interval = 1/(frames/ellapsed)
        resolution_interval = (KEMEvaluation.RESOLUTION * estimated_interval) / self.interval
        logging.info ('Estimation Task for ' + str(ellapsed/60) + ' minutes video duration with estimated interval ' + str(estimated_interval))
        samples = 0
        window_error_position = 0
        window_error_velocity = 0
        k = 0
        for i in range(len(self.ground_truth)):
            track = self.trajectories[i]
            if self.initial_time is None:
                self.initial_time = track.utm.timestamp
            gt = self.ground_truth[i]
            self.confusion_matrix[self.category][track.classification.elected[0].id] += 1
            self.mcc_table [self.category][0]+=1
            self.mcc_table [self.category][1]+=1
            if self.category == track.classification.elected[0].id:
                self.mcc_table[self.category][2]+=1    
            x_track,y_track = track.utm.position
            vx_track, vy_track = track.utm.velocity 
            estimated_lat, estimated_lon, estimated_speed, estimated_course, self.bearing, self.distance_from_camera, bbox = track.get_current_kinematic()
            samples+=1
            window_error_position += math.sqrt(math.pow(x_track - gt.x,2) + math.pow(y_track - gt.y,2))
            window_error_velocity += math.sqrt(math.pow(vx_track - gt.vx,2) + math.pow(vy_track - gt.vy,2))
        k = k+1
        error_position = window_error_position * (1/samples)
        error_velocity = window_error_velocity * (1/samples)
        self.mse_overall_results.append ([resolution_interval * (k), (estimated_lat,estimated_lon,estimated_speed,estimated_course), (gt.lat,gt.lng,gt.speed,gt.course), error_position, error_velocity])
        window_error_position = 0
        window_error_velocity = 0
        samples = 0
