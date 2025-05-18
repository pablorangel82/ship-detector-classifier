import math
import logging
from ultralytics import YOLO
import logging
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
from core.estimation_submodule import Kinematic
class TMMEvaluation:
    FPS = 15
    def __init__(self, category, test_case):
        self.path = 'evaluation/trials/tmm/'+str(test_case)+'/'
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
        logging.info ('Detection / Classification Task')
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
            Kinematic.SIMULATED_DT = gt.delta_t
            
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
            
            window_error_position = []
            window_error_speed = []
            window_error_course = []
            total_error_position = []
            total_error_speed = []
            total_error_course = []

  
            percentile = 95
            total_duration = 0
            first_track = None
            tracks_str = ''
            results = ''
            duration_in_seconds = 0
            qty = 0
            previous_frame = 0
            for frame in values:
                qty+=1
                track = values[frame]
                
                gt = self.ground_truth[frame]
                if first_track is None:
                    first_track = track

                # if gt.estimated is True:
                #     continue

                tracks_str += str(track.lat) + ',' +str(track.lon) + ',' + str(track.speed) + ',' + str(track.course) + '\n'
                
                self.confusion_matrix[self.category][track.classification.elected[0].id] += 1
                self.mcc_table [self.category][0]+=1
                self.mcc_table [track.classification.elected[0].id][1]+=1
                if self.category == track.classification.elected[0].id:
                    self.mcc_table[self.category][2]+=1    
               
                pos_error = math.sqrt(math.pow(track.x - gt.x,2) + math.pow(track.y - gt.y,2))
                window_error_position.append(pos_error)
                total_error_position.append(pos_error)

                speed_error = math.sqrt(math.pow(track.speed - gt.speed,2)) 
                window_error_speed.append (speed_error)
                total_error_speed.append(speed_error)
                
                course_error = abs((track.course - gt.course + 180) % 360 - 180) 
                window_error_course.append (course_error)
                total_error_course.append(course_error)
                
                delta_frame = frame - previous_frame
                previous_frame = frame
                duration_in_seconds += delta_frame / TMMEvaluation.FPS
                total_duration = frame / TMMEvaluation.FPS
                #print(track.lat, track.lon, gt.lat, gt.lng)
                if duration_in_seconds > 10 or qty == (len(values)-1): #or (len(values)-1 == total_samples):
                    # window_vel_diff.sort()
                    # window_pos_diff.sort()
                    # end = int(len(window_vel_diff) * 0.8)
                    # window_vel_diff_cut = window_vel_diff [0:end]
                    # window_pos_diff_cut = window_pos_diff [0:end]

                    # run_vel_diff.sort()
                    # run_pos_diff.sort()
                    # end = int(len(run_vel_diff) * 0.8)
                    # run_vel_diff_cut = run_vel_diff [0:end]
                    # run_pos_diff_cut = run_pos_diff [0:end]

                    first_track = track
                   
                    metric.typical_classification_metrics(self.categories,self.confusion_matrix)
              
                    rmse_window_error_position = metric.rmse(metric.values_bellow_percentile(window_error_position,percentile))
                    rmse_window_error_speed = metric.rmse(metric.values_bellow_percentile(window_error_speed,percentile))
                    rmse_window_error_course = metric.rmse(metric.values_bellow_percentile(window_error_course,percentile))
                    
                    rmse_total_error_position = metric.rmse(metric.values_bellow_percentile(total_error_position,percentile))
                    rmse_total_error_speed = metric.rmse(metric.values_bellow_percentile(total_error_speed,percentile))
                    rmse_total_error_course = metric.rmse(metric.values_bellow_percentile(total_error_course,percentile))

                    window_error_course.clear()
                    window_error_speed.clear()
                    window_error_position.clear()
                    
                    duration_in_seconds = 0
                
                    results += str(total_duration) + ',' + str(rmse_total_error_position) + ',' + str(rmse_total_error_speed) + ',' + str(rmse_total_error_course) + ','
                    results += str(rmse_window_error_position) + ',' + str(rmse_window_error_speed) + ',' + str(rmse_window_error_course) + ','
                    results += str(metric.accs[self.category]) + '\n'#',' + str(metric.precs[self.category]) + ',' + str(metric.recalls[self.category]) + ',' +str(metric.f1s[self.category]) + '\n'
                    print(metric.precs[self.category])
            path_to_save = os.path.join(self.path,'tracks/',key +'.csv')   
            tfile = codecs.open(path_to_save, 'w', 'utf-8') 
          #  tfile.write(tracks_str)
            tfile.close()
            #print(results)
            path_to_save = os.path.join(self.path,'results/',key+'_result.csv')        
            tFile = codecs.open(path_to_save, 'w', 'utf-8')
           # tFile.write(results)
            tFile.close()