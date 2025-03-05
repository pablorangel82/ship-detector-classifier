import math
import logging
from ultralytics import YOLO
import logging
from datetime import datetime
import copy
from core.dcm import DCM
from evaluation.ground_truth import GroundTruth
from core.listener import Listener

class KEMEvaluation (Listener):
    RESOLUTION = 30
    def __init__(self, category, confusion_matrix, mcc_table, interval):
        self.current_id_test_case = -1
        self.trajectories = []
        self.ground_truth = []
        self.category = category
        self.confusion_matrix = confusion_matrix
        self.mcc_table = mcc_table
        self.initial_time = None
        self.interval = interval
        self.mse_overall_results = {}

    def add_test_case(self, id_test_case):
        self.current_id_test_case = id_test_case
        self.trajectories.append({})
        self.ground_truth.append([])
       
    def receive_evt(self, img, track, evt_type):
        trajectory = None
        try:
            trajectory = self.trajectories[self.current_id_test_case][track.uuid]
        except:
            trajectory = []
        trajectory.append(track)
        self.trajectories[self.current_id_test_case][track.uuid] = trajectory
    
    def evaluate(self, test_case, config_path, version):
        dcm = DCM(config_path, str(version), 'en')
        dcm.listener = self
        gt = GroundTruth(-22.899988197673935, -43.160415545734416,67,8,355,0,26.5)
        self.ground_truth[test_case].append(gt)
        logging.info ('Detection / Classification Task')
        it = datetime.now()
        frames = 0
        while True:
            frames +=1
            bearing = gt.bearing
            azimuth = gt.azimuth
            physical_zoom = gt.physical_zoom
            dcm.camera.set_to_track_position(bearing, azimuth,physical_zoom)
            begin_detection = datetime.now()
            img_to_show,tracks_list = dcm.detect_estimate_and_classify()
            end_detection = datetime.now()
            if img_to_show is None and tracks_list is None:
                break
            delta_t = (end_detection - begin_detection).seconds
            gt = copy.deepcopy(gt)
            gt.estimate(delta_t)
            self.ground_truth[test_case].append(gt)
        ft = datetime.now()
        ellapsed = (ft - it).seconds
        estimated_interval = 1/(frames/ellapsed)
        resolution_interval = (KEMEvaluation.RESOLUTION * estimated_interval) / self.interval
        logging.info ('Estimation Task for ' + str(ellapsed/60) + ' minutes video duration with estimated interval ' + str(estimated_interval))
        for i in range(len(self.trajectories)):
            samples = 0
            window_error_position = 0
            window_error_velocity = 0
            for trajectory in self.trajectories[i].values():
                delta_t = 0
                k = 0
                for j in range(len(self.ground_truth[i])):
                    if j > len(trajectory)-1:
                        break
                    track = trajectory[j]
                    if self.initial_time is None:
                        self.initial_time = track.kinematic.timestamp
                    gt = self.ground_truth[i][j]
                    self.confusion_matrix[self.category][track.classification.category.id] += 1
                    self.mcc_table [self.category][0]+=1
                    self.mcc_table [self.category][1]+=1
                    if self.category == track.classification.category.id:
                        self.mcc_table[self.category][2]+=1    
                    x_track,y_track = track.kinematic.geo_positions.get_current_value()
                    vx_track, vy_track = track.kinematic.velocities.get_current_value() 
                    estimated_lat, estimated_lon, estimated_speed, estimated_course, self.bearing, self.distance_from_camera, bbox = track.kinematic.get_current_kinematic()
                    samples+=1
                    window_error_position += math.sqrt(math.pow(x_track - gt.x,2) + math.pow(y_track - gt.y,2))
                    window_error_velocity += math.sqrt(math.pow(vx_track - gt.vx,2) + math.pow(vy_track - gt.vy,2))
                    delta_t = delta_t +self.interval
                    if delta_t >= resolution_interval:
                        k = k+1
                        error_position = window_error_position * (1/samples)
                        error_velocity = window_error_velocity * (1/samples)
                        try:
                            reg = self.mse_overall_results[track.uuid]
                        except:
                            reg = []
                        reg.append ([resolution_interval * (k), (estimated_lat,estimated_lon,estimated_speed,estimated_course), (gt.lat,gt.lng,gt.speed,gt.course), error_position, error_velocity])
                        self.mse_overall_results[track.uuid] = reg
                        delta_t = 0
                        window_error_position = 0
                        window_error_velocity = 0
                        samples = 0
