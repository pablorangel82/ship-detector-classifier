from glob import glob
import math
import pandas as pd
import glob
from core.dcm import DCM
from evaluation.ground_truth import GroundTruth
import os
from core.viewer import view
import cv2
from core.converter import Converter
import codecs
from core.category import Category
import numpy as np
from evaluation.metrics import Metric
from core.estimation_submodule import LinearKinematic
from evaluation.results import SaveResults

class TMMEvaluation:
    FPS = 15
    all_distance = []
    all_pos_error = []
    all_speed_error = []
    all_course_error = []

    def __init__(self, category, test_case):
        self.path = '../report/evaluation/trials/tmm/'+str(test_case)+'/'
        self.test_case = test_case
        for item in os.listdir(self.path+'/results'):
            pc = os.path.join(self.path+'/results', item)
            if os.path.isfile(pc):
                os.remove(pc)
        for item in os.listdir(self.path+'/tracks'):
            pc = os.path.join(self.path+'/tracks', item)
            if os.path.isfile(pc):
                os.remove(pc)
                
        self.category = category
        self.categories = Category.load_categories('en')
        self.trajectories = {}
        self.ground_truth = []
        self.confusion_matrix = np.zeros((len(self.categories),len(self.categories)), dtype=np.int64) 
        self.mcc_table  = np.zeros((len(self.categories),3), dtype=np.int64)
        self.current_frame = 0
        self.std_delta_t = 0.15

    def read_ground_truth(self,path):
        file_path = os.path.join(path,'kinematic.csv')
        old_gt = None
        with open(file_path, 'r') as file:
            next(file)
            for line in file:
                values = line.split(',')      
                gt = GroundTruth(values[2], float(values[3]), float(values[4]), float(values[5]), values[6], float(values[7]), float(values[8]), float(values[9]))
                if old_gt is not None:
                    gt.delta_t = (gt.timestamp.timestamp() - old_gt.timestamp.timestamp())
                    self.ground_truth.append(gt)
                gt.x = gt.x + ((gt.vx / 1.944) * gt.delta_t)
                gt.y = gt.y + ((gt.vy / 1.944) * gt.delta_t)
                gt.lat, gt.lng = Converter.xy_to_geo(gt.x,gt.y)
                gt.estimated = True
                old_gt = gt

    def evaluate(self):
        dcm = DCM(self.path+'config','en')
        dcm.start()
        self.read_ground_truth(self.path)
        self.current_frame = 0
        metric = Metric()
        while True:
            try:
                gt = self.ground_truth[self.current_frame]
            except:
                break
           # bearing, distance = Converter.geo_to_polar(dcm.camera.lat,dcm.camera.lon, gt.lat, gt.lng)
           # dcm.camera.set_to_track_position(bearing,distance)
            dcm.camera.convert_ptz_to_polar(gt.pan, gt.tilt, gt.zoom)
            LinearKinematic.SIMULATED_DT = gt.delta_t
            
            img_to_show,tracks_list = dcm.detect_estimate_and_classify()
            if tracks_list is not None:
                for uuid in tracks_list:
                    try:
                        trajectory = self.trajectories [uuid]
                    except:
                        trajectory = {}
                        self.trajectories[uuid] = trajectory
                    trajectory [self.current_frame] = tracks_list[uuid] 
            self.current_frame +=1
            if img_to_show is None:
                break
            view(img_to_show, tracks_list, dcm.camera)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            
        for key in self.trajectories:
            print(key)
            values = self.trajectories[key]
            
            window_error_position_quad = np.array([])
            window_stddev_position = np.array([])
            window_error_speed_quad = np.array([])
            window_stddev_speed = np.array([])
            window_error_course_quad = np.array([])
            window_stddev_course = np.array([])
            total_error_position_quad = np.array([])
            total_stddev_position = np.array([])
            total_error_speed_quad = np.array([])
            total_stddev_speed = np.array([])
            total_error_course_quad = np.array([])
            total_stddev_course = np.array([])
            
            window_nees = np.array([])

            window_error_position_abs = np.array([])
            window_error_speed_abs = np.array([])
            window_error_course_abs = np.array([])
            total_error_position_abs = np.array([])
            total_error_speed_abs = np.array([])
            total_error_course_abs = np.array([])
            
            rmse_total_error_position_graph_0 = np.array([])
            rmse_total_stddev_position_graph_0 = np.array([])
            rmse_total_error_speed_graph_0= np.array([])
            rmse_total_stddev_speed_graph_0 = np.array([])
            rmse_total_error_course_graph_0= np.array([])
            rmse_total_stddev_course_graph_0 = np.array([])
            rmse_window_error_position_graph_0 = np.array([])
            rmse_window_stddev_position_graph_0 = np.array([])
            rmse_window_error_speed_graph_0= np.array([])
            rmse_window_stddev_speed_graph_0 = np.array([])
            rmse_window_error_course_graph_0= np.array([])
            rmse_window_stddev_course_graph_0 = np.array([])

            
            rmse_total_error_position_graph_5 = np.array([])
            rmse_total_stddev_position_graph_5 = np.array([])
            rmse_total_error_speed_graph_5= np.array([])
            rmse_total_stddev_speed_graph_5 = np.array([])
            rmse_total_error_course_graph_5= np.array([])
            rmse_total_stddev_course_graph_5 = np.array([])
            rmse_window_error_position_graph_5 = np.array([])
            rmse_window_stddev_position_graph_5 = np.array([])
            rmse_window_error_speed_graph_5= np.array([])
            rmse_window_stddev_speed_graph_5 = np.array([])
            rmse_window_error_course_graph_5= np.array([])
            rmse_window_stddev_course_graph_5 = np.array([])

            rmse_total_error_position_graph_10 = np.array([])
            rmse_total_stddev_position_graph_10 = np.array([])
            rmse_total_error_speed_graph_10= np.array([])
            rmse_total_stddev_speed_graph_10 = np.array([])
            rmse_total_error_course_graph_10= np.array([])
            rmse_total_stddev_course_graph_10 = np.array([])
            rmse_window_error_position_graph_10 = np.array([])
            rmse_window_stddev_position_graph_10 = np.array([])
            rmse_window_error_speed_graph_10= np.array([])
            rmse_window_stddev_speed_graph_10 = np.array([])
            rmse_window_error_course_graph_10= np.array([])
            rmse_window_stddev_course_graph_10 = np.array([])

            rmse_total_error_position_graph_20 = np.array([])
            rmse_total_stddev_position_graph_20 = np.array([])
            rmse_total_error_speed_graph_20= np.array([])
            rmse_total_stddev_speed_graph_20 = np.array([])
            rmse_total_error_course_graph_20= np.array([])
            rmse_total_stddev_course_graph_20 = np.array([])
            rmse_window_error_position_graph_20 = np.array([])
            rmse_window_stddev_position_graph_20 = np.array([])
            rmse_window_error_speed_graph_20= np.array([])
            rmse_window_stddev_speed_graph_20 = np.array([])
            rmse_window_error_course_graph_20= np.array([])
            rmse_window_stddev_course_graph_20 = np.array([])
            
            cov_window_position_graph = []

            nees_window_graph_0 = np.array([])
            nees_window_graph_5 = np.array([])
            nees_window_graph_10 = np.array([])
            nees_window_graph_20 = np.array([])

            x_path_gt = []
            y_path_gt = []
            x_path_track = []
            y_path_track = []
            
            self.confusion_matrix = np.zeros((len(self.categories),len(self.categories)), dtype=np.int64) 
            self.mcc_table  = np.zeros((len(self.categories),3), dtype=np.int64)

            total_duration = 0
            first_track = None
            tracks_str = ''
            results_0 = 'total_duration&rmse_total_error_position_0&rmse_total_error_speed_0&rmse_total_error_course_0&rmse_window_error_position_0&rmse_window_error_speed_0&rmse_window_error_course_0&nees \\\\\n'
            results_5 = 'total_duration&rmse_total_error_position_5&rmse_total_error_speed_5&rmse_total_error_course_5&rmse_window_error_position_5&rmse_window_error_speed_5&rmse_window_error_course_5&nees \\\\\n'
            results_10 = 'total_duration&rmse_total_error_position_10&rmse_total_error_speed_10&rmse_total_error_course_10&rmse_window_error_position_10&rmse_window_error_speed_10&rmse_window_error_course_10&nees\\\\\n'
            results_20 = 'total_duration&rmse_total_error_position_20&rmse_total_error_speed_20&rmse_total_error_course_20&rmse_window_error_position_20&rmse_window_error_speed_20&rmse_window_error_course_20&nees\\\\\n'

            duration_in_seconds = 0
            qty = 0
            previous_frame = 0
            windows = []

            for frame in values:
                qty+=1
                track = values[frame]
                
                gt = self.ground_truth[frame]
                if first_track is None:
                    first_track = track

                # if gt.estimated is True:
                #     continue

                tracks_str += str(track.lat) + ';' +str(track.lon) + ';' + str(track.speed) + ';' + str(track.course) + '\n'
                self.confusion_matrix[self.category][track.classification.elected[0].id] += 1
                self.mcc_table [self.category][0]+=1
                self.mcc_table [track.classification.elected[0].id][1]+=1
                if self.category == track.classification.elected[0].id:
                    self.mcc_table[self.category][2]+=1    
               
                dx = track.utm.position[0] - gt.x
                dy = track.utm.position[1] - gt.y
                dvx = track.utm.velocity[0] - gt.vx 
                dvy = track.utm.velocity[1] - gt.vy

                e = np.array([
                    dx,   # x_true - x_est
                    dvx,  # vx_true - vx_est
                    dy,   # y_true - y_est
                    dvy   # vy_true - vy_est
                ])
                P = track.utm.kf.P
                nees = e.T @ np.linalg.solve(P, e)

                pos_error_quad = dx**2 + dy**2
                window_error_position_quad = np.concatenate((window_error_position_quad, [pos_error_quad]))
                total_error_position_quad = np.concatenate((total_error_position_quad, [pos_error_quad]))
                
                distance = np.sqrt(dx**2 + dy**2)
                
                pos_error_abs =abs(track.x - gt.x) + abs(track.y - gt.y)
                window_error_position_abs = np.concatenate((window_error_position_abs, [pos_error_abs]))
                total_error_position_abs = np.concatenate((total_error_position_abs, [pos_error_abs]))

                pos_error = math.hypot(dx, dy)
                window_stddev_position = np.concatenate((window_stddev_position, [pos_error]))
                total_stddev_position = np.concatenate((total_stddev_position, [pos_error]))

                speed_error_quad = math.pow(track.speed - gt.speed,2)
                window_error_speed_quad = np.concatenate((window_error_speed_quad, [speed_error_quad]))
                total_error_speed_quad = np.concatenate((total_error_speed_quad, [speed_error_quad]))
                
                speed_error_abs = abs(track.speed - gt.speed) 
                window_error_speed_abs = np.concatenate((window_error_speed_abs, [speed_error_abs]))
                total_error_speed_abs = np.concatenate((total_error_speed_abs, [speed_error_abs]))

                speed_error = track.speed - gt.speed
                window_stddev_speed = np.concatenate((window_stddev_speed, [speed_error]))
                total_stddev_speed = np.concatenate((total_stddev_speed, [speed_error]))

                course_error_quad = math.pow(((track.course - gt.course + 180) % 360) - 180,2) 
                window_error_course_quad = np.concatenate((window_error_course_quad, [course_error_quad]))
                total_error_course_quad = np.concatenate((total_error_course_quad, [course_error_quad]))
                
                course_error_abs = abs((track.course - gt.course + 180) % 360 - 180) 
                window_error_course_abs = np.concatenate((window_error_course_abs, [course_error_abs]))
                total_error_course_abs = np.concatenate((total_error_course_abs, [course_error_abs]))
                
                course_error = ((track.course - gt.course + 180) % 360) - 180
                window_stddev_course = np.concatenate((window_stddev_course, [course_error]))
                total_stddev_course = np.concatenate((total_stddev_course, [course_error]))

                window_nees = np.concatenate((window_nees, [nees]))

                delta_frame = frame - previous_frame
                previous_frame = frame
                duration_in_seconds += delta_frame / TMMEvaluation.FPS
                total_duration = frame / TMMEvaluation.FPS

                if duration_in_seconds > 10 or qty == (len(values)-1): #or (len(values)-1 == total_samples):
                    windows.append(round(total_duration))
                    x_path_gt.append(gt.x)
                    x_path_track.append(track.x)
                    y_path_gt.append(gt.y)
                    y_path_track.append(track.y)

                    P_pos = track.utm.kf.P[np.ix_([0,2],[0,2])]

                    P_pos = 0.5 * (P_pos + P_pos.T)
                    eigvals, eigvecs = np.linalg.eigh(P_pos)
                    idx = np.argmax(eigvals)
                    angle = np.arctan2(eigvecs[1, idx], eigvecs[0, idx])
                    scale = np.sqrt(5.991)
                    width  = 2 * scale * np.sqrt(eigvals[0])
                    height = 2 * scale * np.sqrt(eigvals[1])
                    mx = (track.x + gt.x) / 2
                    my = (track.y + gt.y) / 2
                    cov_window_position = (round(total_duration), gt.x, gt.y, track.x, track.y, mx, my, distance, width, height, angle)
                    
                    first_track = track
                   
                    metric.typical_classification_metrics(self.categories,self.confusion_matrix)
              
                    rmse_window_error_position_0 = metric.rmse(metric.values_below_percentile(window_error_position_quad,100))
                    rmse_window_stddev_position_0 = metric.std_sample(metric.values_below_percentile(window_error_position_quad,100))
                    rmse_window_error_speed_0 = metric.rmse(metric.values_below_percentile(window_error_speed_quad,100))
                    rmse_window_stddev_speed_0 = metric.std_sample(metric.values_below_percentile(window_error_speed_quad,100))
                    rmse_window_error_course_0 = metric.rmse(metric.values_below_percentile(window_error_course_quad,100))
                    rmse_window_stddev_course_0 = metric.std_sample(metric.values_below_percentile(window_error_course_quad,100))
                    rmse_window_error_position_graph_0 = np.concatenate((rmse_window_error_position_graph_0, [rmse_window_error_position_0]))
                    rmse_window_stddev_position_graph_0 = np.concatenate((rmse_window_stddev_position_graph_0, [rmse_window_stddev_position_0]))
                    rmse_window_error_speed_graph_0 = np.concatenate((rmse_window_error_speed_graph_0, [rmse_window_error_speed_0]))
                    rmse_window_stddev_speed_graph_0 = np.concatenate((rmse_window_stddev_speed_graph_0, [rmse_window_stddev_speed_0]))
                    rmse_window_error_course_graph_0 = np.concatenate((rmse_window_error_course_graph_0, [rmse_window_error_course_0]))
                    rmse_window_stddev_course_graph_0 = np.concatenate((rmse_window_stddev_course_graph_0, [rmse_window_stddev_course_0]))
                    nees_window_0 = np.mean(metric.values_below_percentile(window_nees,100))
                    nees_window_graph_0 = np.concatenate((nees_window_graph_0, [nees_window_0]))

                    cov_window_position_graph.append(cov_window_position)
                    
                    rmse_total_error_position_0 = metric.rmse(metric.values_below_percentile(total_error_position_quad,100))
                    rmse_total_stddev_position_0 = metric.std_sample(metric.values_below_percentile(total_error_position_quad,100))
                    rmse_total_error_speed_0 = metric.rmse(metric.values_below_percentile(total_error_speed_quad,100))
                    rmse_total_stddev_speed_0 = metric.std_sample(metric.values_below_percentile(total_error_speed_quad,100))
                    rmse_total_error_course_0 = metric.rmse(metric.values_below_percentile(total_error_course_quad,100))
                    rmse_total_stddev_course_0 = metric.std_sample(metric.values_below_percentile(total_error_course_quad,100))
                    rmse_total_error_position_graph_0 = np.concatenate((rmse_total_error_position_graph_0, [rmse_total_error_position_0]))
                    rmse_total_stddev_position_graph_0 = np.concatenate((rmse_total_stddev_position_graph_0, [rmse_total_stddev_position_0]))
                    rmse_total_error_speed_graph_0 = np.concatenate((rmse_total_error_speed_graph_0, [rmse_total_error_speed_0]))
                    rmse_total_stddev_speed_graph_0 = np.concatenate((rmse_total_stddev_speed_graph_0, [rmse_total_stddev_speed_0]))
                    rmse_total_error_course_graph_0 = np.concatenate((rmse_total_error_course_graph_0, [rmse_total_error_course_0]))
                    rmse_total_stddev_course_graph_0 = np.concatenate((rmse_total_stddev_course_graph_0, [rmse_total_stddev_course_0]))
                 

                    rmse_window_error_position_5 = metric.rmse(metric.values_below_percentile(window_error_position_quad,95))
                    rmse_window_stddev_position_5 = metric.std_sample(metric.values_below_percentile(window_error_position_quad,95))
                    rmse_window_error_speed_5 = metric.rmse(metric.values_below_percentile(window_error_speed_quad,95))
                    rmse_window_stddev_speed_5 = metric.std_sample(metric.values_below_percentile(window_error_speed_quad,95))
                    rmse_window_error_course_5 = metric.rmse(metric.values_below_percentile(window_error_course_quad,95))
                    rmse_window_stddev_course_5 = metric.std_sample(metric.values_below_percentile(window_error_course_quad,95))
                    rmse_window_error_position_graph_5 = np.concatenate((rmse_window_error_position_graph_5, [rmse_window_error_position_5]))
                    rmse_window_stddev_position_graph_5 = np.concatenate((rmse_window_stddev_position_graph_5, [rmse_window_stddev_position_5]))
                    rmse_window_error_speed_graph_5 = np.concatenate((rmse_window_error_speed_graph_5, [rmse_window_error_speed_5]))
                    rmse_window_stddev_speed_graph_5 = np.concatenate((rmse_window_stddev_speed_graph_5, [rmse_window_stddev_speed_5]))
                    rmse_window_error_course_graph_5 = np.concatenate((rmse_window_error_course_graph_5, [rmse_window_error_course_5]))
                    rmse_window_stddev_course_graph_5 = np.concatenate((rmse_window_stddev_course_graph_5, [rmse_window_stddev_course_5]))
                    nees_window_5 = np.mean(metric.values_below_percentile(window_nees,95))
                    nees_window_graph_5 = np.concatenate((nees_window_graph_5, [nees_window_5]))
                    
                    rmse_total_error_position_5 = metric.rmse(metric.values_below_percentile(total_error_position_quad,95))
                    rmse_total_stddev_position_5 = metric.std_sample(metric.values_below_percentile(total_error_position_quad,95))
                    rmse_total_error_speed_5 = metric.rmse(metric.values_below_percentile(total_error_speed_quad,95))
                    rmse_total_stddev_speed_5 = metric.std_sample(metric.values_below_percentile(total_error_speed_quad,95))
                    rmse_total_error_course_5 = metric.rmse(metric.values_below_percentile(total_error_course_quad,95))
                    rmse_total_stddev_course_5 = metric.std_sample(metric.values_below_percentile(total_error_course_quad,95))
                    rmse_total_error_position_graph_5 = np.concatenate((rmse_total_error_position_graph_5, [rmse_total_error_position_5]))
                    rmse_total_stddev_position_graph_5 = np.concatenate((rmse_total_stddev_position_graph_5, [rmse_total_stddev_position_5]))
                    rmse_total_error_speed_graph_5 = np.concatenate((rmse_total_error_speed_graph_5, [rmse_total_error_speed_5]))
                    rmse_total_stddev_speed_graph_5 = np.concatenate((rmse_total_stddev_speed_graph_5, [rmse_total_stddev_speed_5]))
                    rmse_total_error_course_graph_5 = np.concatenate((rmse_total_error_course_graph_5, [rmse_total_error_course_5]))
                    rmse_total_stddev_course_graph_5 = np.concatenate((rmse_total_stddev_course_graph_5, [rmse_total_stddev_course_5]))
                    
                    rmse_window_error_position_10 = metric.rmse(metric.values_below_percentile(window_error_position_quad,90))
                    rmse_window_stddev_position_10 = metric.std_sample(metric.values_below_percentile(window_error_position_quad,90))
                    rmse_window_error_speed_10 = metric.rmse(metric.values_below_percentile(window_error_speed_quad,90))
                    rmse_window_stddev_speed_10 = metric.std_sample(metric.values_below_percentile(window_error_speed_quad,90))
                    rmse_window_error_course_10 = metric.rmse(metric.values_below_percentile(window_error_course_quad,90))
                    rmse_window_stddev_course_10 = metric.std_sample(metric.values_below_percentile(window_error_course_quad,90))
                    rmse_window_error_position_graph_10 = np.concatenate((rmse_window_error_position_graph_10, [rmse_window_error_position_10]))
                    rmse_window_stddev_position_graph_10 = np.concatenate((rmse_window_stddev_position_graph_10, [rmse_window_stddev_position_10]))
                    rmse_window_error_speed_graph_10 = np.concatenate((rmse_window_error_speed_graph_10, [rmse_window_error_speed_10]))
                    rmse_window_stddev_speed_graph_10 = np.concatenate((rmse_window_stddev_speed_graph_10, [rmse_window_stddev_speed_10]))
                    rmse_window_error_course_graph_10 = np.concatenate((rmse_window_error_course_graph_10, [rmse_window_error_course_10]))
                    rmse_window_stddev_course_graph_10 = np.concatenate((rmse_window_stddev_course_graph_10, [rmse_window_stddev_course_10]))
                    nees_window_10 = np.mean(metric.values_below_percentile(window_nees,90))
                    nees_window_graph_10 = np.concatenate((nees_window_graph_10, [nees_window_10]))
                    
                    rmse_total_error_position_10 = metric.rmse(metric.values_below_percentile(total_error_position_quad,90))
                    rmse_total_stddev_position_10 = metric.std_sample(metric.values_below_percentile(total_error_position_quad,90))
                    rmse_total_error_speed_10 = metric.rmse(metric.values_below_percentile(total_error_speed_quad,90))
                    rmse_total_stddev_speed_10 = metric.std_sample(metric.values_below_percentile(total_error_speed_quad,90))
                    rmse_total_error_course_10 = metric.rmse(metric.values_below_percentile(total_error_course_quad,90))
                    rmse_total_stddev_course_10 = metric.std_sample(metric.values_below_percentile(total_error_course_quad,90))
                    rmse_total_error_position_graph_10 = np.concatenate((rmse_total_error_position_graph_10, [rmse_total_error_position_10]))
                    rmse_total_stddev_position_graph_10 = np.concatenate((rmse_total_stddev_position_graph_10, [rmse_total_stddev_position_10]))
                    rmse_total_error_speed_graph_10 = np.concatenate((rmse_total_error_speed_graph_10, [rmse_total_error_speed_10]))
                    rmse_total_stddev_speed_graph_10 = np.concatenate((rmse_total_stddev_speed_graph_10, [rmse_total_stddev_speed_10]))
                    rmse_total_error_course_graph_10 = np.concatenate((rmse_total_error_course_graph_10, [rmse_total_error_course_10]))
                    rmse_total_stddev_course_graph_10 = np.concatenate((rmse_total_stddev_course_graph_10, [rmse_total_stddev_course_10]))
                   
                    rmse_window_error_position_20 = metric.rmse(metric.values_below_percentile(window_error_position_quad,80))
                    rmse_window_stddev_position_20 = metric.std_sample(metric.values_below_percentile(window_error_position_quad,80))
                    rmse_window_error_speed_20 = metric.rmse(metric.values_below_percentile(window_error_speed_quad,80))
                    rmse_window_stddev_speed_20 = metric.std_sample(metric.values_below_percentile(window_error_speed_quad,80))
                    rmse_window_error_course_20 = metric.rmse(metric.values_below_percentile(window_error_course_quad,80))
                    rmse_window_stddev_course_20 = metric.std_sample(metric.values_below_percentile(window_error_course_quad,80))
                    rmse_window_error_position_graph_20 = np.concatenate((rmse_window_error_position_graph_20, [rmse_window_error_position_20]))
                    rmse_window_stddev_position_graph_20 = np.concatenate((rmse_window_stddev_position_graph_20, [rmse_window_stddev_position_20]))
                    rmse_window_error_speed_graph_20 = np.concatenate((rmse_window_error_speed_graph_20, [rmse_window_error_speed_20]))
                    rmse_window_stddev_speed_graph_20 = np.concatenate((rmse_window_stddev_speed_graph_20, [rmse_window_stddev_speed_20]))
                    rmse_window_error_course_graph_20 = np.concatenate((rmse_window_error_course_graph_20, [rmse_window_error_course_20]))
                    rmse_window_stddev_course_graph_20 = np.concatenate((rmse_window_stddev_course_graph_20, [rmse_window_stddev_course_20]))
                    nees_window_20 = np.mean(metric.values_below_percentile(window_nees,80))
                    nees_window_graph_20 = np.concatenate((nees_window_graph_20, [nees_window_20]))
                    
                    rmse_total_error_position_20 = metric.rmse(metric.values_below_percentile(total_error_position_quad,80))
                    rmse_total_stddev_position_20 = metric.std_sample(metric.values_below_percentile(total_error_position_quad,80))
                    rmse_total_error_speed_20 = metric.rmse(metric.values_below_percentile(total_error_speed_quad,80))
                    rmse_total_stddev_speed_20 = metric.std_sample(metric.values_below_percentile(total_error_speed_quad,80))
                    rmse_total_error_course_20 = metric.rmse(metric.values_below_percentile(total_error_course_quad,80))
                    rmse_total_stddev_course_20 = metric.std_sample(metric.values_below_percentile(total_error_course_quad,80))
                    rmse_total_error_position_graph_20 = np.concatenate((rmse_total_error_position_graph_20, [rmse_total_error_position_20]))
                    rmse_total_stddev_position_graph_20 = np.concatenate((rmse_total_stddev_position_graph_20, [rmse_total_stddev_position_20]))
                    rmse_total_error_speed_graph_20 = np.concatenate((rmse_total_error_speed_graph_20, [rmse_total_error_speed_20]))
                    rmse_total_stddev_speed_graph_20 = np.concatenate((rmse_total_stddev_speed_graph_20, [rmse_total_stddev_speed_20]))
                    rmse_total_error_course_graph_20 = np.concatenate((rmse_total_error_course_graph_20, [rmse_total_error_course_20]))
                    rmse_total_stddev_course_graph_20 = np.concatenate((rmse_total_stddev_course_graph_20, [rmse_total_stddev_course_20]))
                  
                    window_error_course_quad= np.array([])
                    window_error_speed_quad = np.array([])
                    window_error_position_quad = np.array([])
                    
                    window_error_course_abs = np.array([])
                    window_error_speed_abs = np.array([])
                    window_error_position_abs = np.array([])

                    window_stddev_position = np.array([])
                    window_stddev_speed = np.array([])
                    window_stddev_course = np.array([])

                    window_nees = np.array([])
                    window_nees = np.array([])
                    
                    duration_in_seconds = 0
                
             

                    results_0 += f'{str(round(total_duration))} & {str(round(rmse_total_error_position_0,2))} & {str(round(rmse_total_error_speed_0,2))} & {str(round(rmse_total_error_course_0,2))} & '
                    results_0 += f'{str(round(rmse_window_error_position_0,2))} & {str(round(rmse_window_error_speed_0,2))} & {str(round(rmse_window_error_course_0,2))} & '
                    results_0 += f'{str(round(nees_window_0,2))}\\\\\n'

                    results_5 += f'{str(round(total_duration))} & {str(round(rmse_total_error_position_5,2))} & {str(round(rmse_total_error_speed_5,2))} & {str(round(rmse_total_error_course_5,2))} & '
                    results_5 += f'{str(round(rmse_window_error_position_5,2))} & {str(round(rmse_window_error_speed_5,2))} & {str(round(rmse_window_error_course_5,2))} & '
                    results_5 += f'{str(round(nees_window_5,2))}\\\\\n'

                    results_10 += f'{str(round(total_duration))} & {str(round(rmse_total_error_position_10,2))} & {str(round(rmse_total_error_speed_10,2))} & {str(round(rmse_total_error_course_10,2))} & '
                    results_10 += f'{str(round(rmse_window_error_position_10,2))} & {str(round(rmse_window_error_speed_10,2))} & {str(round(rmse_window_error_course_10,2))} & '
                    results_10 += f'{str(round(nees_window_10,2))}\\\\\n'

                    results_20 += f'{str(round(total_duration))} & {str(round(rmse_total_error_position_20,2))} & {str(round(rmse_total_error_speed_20,2))} & {str(round(rmse_total_error_course_20,2))} & '
                    results_20 += f'{str(round(rmse_window_error_position_20,2))} & {str(round(rmse_window_error_speed_20,2))} & {str(round(rmse_window_error_course_20,2))} &'
                    results_20 += f'{str(round(nees_window_20,2))}\\\\\n'
           
            if len(windows) > 5:  
               
                SaveResults.plot_trajectory_comparison(cov_window_position_graph,self.path,self.test_case)
                SaveResults.plot_rmse('Aggregated RMSE', 'Position', 'meters', windows, rmse_total_error_position_graph_0, rmse_total_error_position_graph_5, rmse_total_error_position_graph_10, rmse_total_error_position_graph_20,self.path,self.test_case)
                SaveResults.plot_rmse('Windowed RMSE', 'Position', 'meters', windows, rmse_window_error_position_graph_0, rmse_window_error_position_graph_5, rmse_window_error_position_graph_10, rmse_window_error_position_graph_20,self.path,self.test_case)
                SaveResults.plot_rmse('Aggregated RMSE', 'Speed', 'knots', windows, rmse_total_error_speed_graph_0, rmse_total_error_speed_graph_5, rmse_total_error_speed_graph_10, rmse_total_error_speed_graph_20,self.path,self.test_case)
                SaveResults.plot_rmse('Windowed RMSE', 'Speed', 'knots', windows, rmse_window_error_speed_graph_0, rmse_window_error_speed_graph_5, rmse_window_error_speed_graph_10, rmse_window_error_speed_graph_20,self.path,self.test_case)
                SaveResults.plot_rmse('Aggregated RMSE', 'Course', 'degrees', windows, rmse_total_error_course_graph_0, rmse_total_error_course_graph_5, rmse_total_error_course_graph_10, rmse_total_error_course_graph_20,self.path,self.test_case)
                SaveResults.plot_rmse('Windowed RMSE', 'Course', 'degrees', windows, rmse_window_error_course_graph_0, rmse_window_error_course_graph_5, rmse_window_error_course_graph_10, rmse_window_error_course_graph_20,self.path,self.test_case)

                
                SaveResults.save_csv_rmse('0',results_0, self.path, self.test_case)
                SaveResults.save_csv_rmse('5',results_5, self.path, self.test_case)   
                SaveResults.save_csv_rmse('10',results_10, self.path, self.test_case)
                SaveResults.save_csv_rmse('20',results_20, self.path, self.test_case)

                
                nees_mean = nees_window_0
                nees_global = f'{str(round(np.mean(nees_mean),2))}'
                path_to_save = os.path.join(self.path,'results/',f'nees_{self.test_case}.csv')        
                tFile = codecs.open(path_to_save, 'w', 'utf-8')
                tFile.write(nees_global)
                tFile.close()
                

                path_to_save = os.path.join(self.path,'tracks/',f'test_{self.test_case}_comp.csv')   
                tfile = codecs.open(path_to_save, 'w', 'utf-8') 
                tfile.write(tracks_str)
                tfile.close()
                
                distance_data = [d[7] for d in cov_window_position_graph]

                
            
                TMMEvaluation.all_distance.extend(distance_data)
                TMMEvaluation.all_pos_error.extend(rmse_total_error_position_graph_0)
                TMMEvaluation.all_speed_error.extend(rmse_total_error_speed_graph_0)
                TMMEvaluation.all_course_error.extend(rmse_total_error_course_graph_0)
              
    @staticmethod
    def general_metrics(root_path):
        base_folders = ['01','02','03','04','05','06']
        results_folder = 'results'
        output_folder = os.path.join(root_path, 'results')
        latex_file = os.path.join(output_folder,'rmse_tables.tex')
        os.makedirs(output_folder, exist_ok=True)
        grouped_rmse_aggregated = {}
        grouped_rmse_windowed = {}
        plot_data_aggregated = {}
        plot_data_windowed = {}
        title_rmse_aggregated = {}
        title_rmse_windowed = {}
        windows_ref = None
        all_nees = []

        for folder in base_folders:
            path = os.path.join(root_path, folder, results_folder)
            csv_rmse_files = glob.glob(os.path.join(path, f'test_{folder}_*.csv'))
            csv_nees_files = glob.glob(os.path.join(path, f'nees_{folder}*.csv'))
            for file in csv_nees_files:
                df = pd.read_csv(file,header=None)
                value = df.values.item()
                all_nees.append(value)
                
            for file in csv_rmse_files:
                filename = os.path.basename(file)
                discard_percent = int(filename.split('_')[-1].replace('.csv',''))
                df = pd.read_csv(file, sep='&', engine='python')
                df = df.replace(r'\\', '', regex=True)
                df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                df = df.apply(pd.to_numeric)
                if windows_ref is None:
                    windows_ref = df.iloc[:,0].values
                if discard_percent not in grouped_rmse_aggregated:
                    grouped_rmse_aggregated[discard_percent] = {
                        'total_error_position': ([], 'm'),
                        'total_error_speed': ([], 'knots'),
                        'total_error_course': ([], 'º')
                    }
                    title_rmse_aggregated[discard_percent] = {
                        'total_error_position':'Aggregated RMSE Position Error',
                        'total_error_speed':'Aggregated RMSE Speed Error',
                        'total_error_course':'Aggregated RMSE Course Error'
                    }
                    grouped_rmse_windowed[discard_percent] = {
                        'window_error_position': ([], 'meters'),
                        'window_error_speed': ([], 'knots'),
                        'window_error_course': ([], 'degrees')
                    }
                    title_rmse_windowed[discard_percent] = {
                        'window_error_position':'Windowed RMSE Position Error',
                        'window_error_speed':'Windowed RMSE Speed Error',
                        'window_error_course':'Windowed RMSE Course Error'
                    }
                
                if discard_percent not in plot_data_windowed:
                    plot_data_windowed[discard_percent] = {
                        'ships': [],
                        'windows': windows_ref,
                        'window_error_position': {},
                        'window_error_speed': {},
                        'window_error_course': {}
                    }
                    plot_data_aggregated[discard_percent] = {
                        'ships': [],
                        'windows': windows_ref,
                        'total_error_position': {},
                        'total_error_speed': {},
                        'total_error_course': {}
                    }

                ship_name = folder

                plot_data_windowed[discard_percent]['ships'].append(ship_name)
                plot_data_windowed[discard_percent]['window_error_position'][ship_name] = df.iloc[:,4].values
                plot_data_windowed[discard_percent]['window_error_speed'][ship_name] = df.iloc[:,5].values
                plot_data_windowed[discard_percent]['window_error_course'][ship_name] = df.iloc[:,6].values

                plot_data_aggregated[discard_percent]['ships'].append(ship_name)
                plot_data_aggregated[discard_percent]['total_error_position'][ship_name] = df.iloc[:,1].values
                plot_data_aggregated[discard_percent]['total_error_speed'][ship_name] = df.iloc[:,2].values
                plot_data_aggregated[discard_percent]['total_error_course'][ship_name] = df.iloc[:,3].values

                grouped_rmse_aggregated[discard_percent]['total_error_position'][0].append(df.iloc[:,1].values)
                grouped_rmse_aggregated[discard_percent]['total_error_speed'][0].append(df.iloc[:,2].values)
                grouped_rmse_aggregated[discard_percent]['total_error_course'][0].append(df.iloc[:,3].values)
                
                grouped_rmse_windowed[discard_percent]['window_error_position'][0].append(df.iloc[:,4].values)
                grouped_rmse_windowed[discard_percent]['window_error_speed'][0].append(df.iloc[:,5].values)
                grouped_rmse_windowed[discard_percent]['window_error_course'][0].append(df.iloc[:,6].values)

        metrics_aggregated = {
            'total_error_position': ('Position Error', 'meters'),
            'total_error_speed': ('Speed Error', 'knots'),
            'total_error_course': ('Course Error', 'degrees')
        }

        metrics_windowed = {
            'window_error_position': ('Position Error', 'meters'),
            'window_error_speed': ('Speed Error', 'knots'),
            'window_error_course': ('Course Error', 'degrees')
        }

     
        SaveResults.plot_mean('Aggregated', metrics_aggregated, grouped_rmse_aggregated, windows_ref, output_folder)
        SaveResults.plot_boxplots('Aggregated', metrics_aggregated, grouped_rmse_aggregated,output_folder)
        SaveResults.plot_mean('Windowed', metrics_windowed,grouped_rmse_windowed, windows_ref, output_folder)
        SaveResults.plot_boxplots('Windowed',metrics_windowed,grouped_rmse_windowed,output_folder)
        SaveResults.plot_errors_by_discard('Aggregated',metrics_aggregated, plot_data_aggregated, output_folder)
        SaveResults.plot_errors_by_discard('Windowed',metrics_windowed, plot_data_windowed, output_folder)
        
        SaveResults.calculate_pearson_correlation(
                TMMEvaluation.all_distance,
                TMMEvaluation.all_pos_error,
                TMMEvaluation.all_speed_error,
                TMMEvaluation.all_course_error,
                output_folder
            )
        SaveResults.plot_nees(all_nees)

       

        print("All figures and LaTeX tables saved in:", output_folder)