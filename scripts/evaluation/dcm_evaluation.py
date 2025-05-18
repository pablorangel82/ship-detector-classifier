from core.dcm import DCM
import logging
import cv2
import codecs
import os
import numpy as np
from core.category import Category
from preparation.dataset_config import DatasetConfig
from evaluation.metrics import Metric


class DCMEvaluation:

    def __init__(self):
        self.test_images_path = os.path.join(DatasetConfig.DATASET_FOLDER,"test/images")
        self.test_labels_path = os.path.join(DatasetConfig.DATASET_FOLDER,"test/labels")
        self.categories = Category.load_categories('en')
        self.confusion_matrix = np.zeros((len(self.categories)-1,len(self.categories)-1), dtype=np.int64) 
        self.mcc_table  = np.zeros((len(self.categories),3), dtype=np.int64)


    def evaluate(self):
        files = os.listdir(self.test_images_path)
        path_to = os.path.join('evaluation/trials/dcm','config')
        dcm = DCM(path_to, 'en')
        i=0
        for i in range(len(files)):
            logging.info('Working on file ' + str(i) + ' of ' + str(len(files)))
            each_file = files[i]
            file_name = each_file.split('.')
            src_img_path = os.path.join(self.test_images_path,each_file)
            src_label_path = os.path.join(self.test_labels_path,file_name[0]+'.txt')
            img = cv2.imread(src_img_path)
            label = codecs.open(src_label_path, 'r', 'utf-8') 
            lines = label.read()
            category_expected = int(lines.split(' ')[0])
            label.close()
            detection_results = dcm.net_classifier.predict([img],verbose=False,conf=dcm.calibration.threshold_confidence, iou=dcm.calibration.threshold_intersection_tracking)
            for result in detection_results:
                for box in result.boxes:
                    confidence = max(box.conf.tolist())
                    index_confidence = box.conf.tolist().index (confidence)
                    category_detected = int(box.cls.tolist()[index_confidence])          
                    if confidence < dcm.calibration.threshold_classification:
                         confidence = 1
                         label = len(self.confusion_matrix[0])
                    self.confusion_matrix[category_expected][category_detected] += 1
                    self.mcc_table [category_expected][0]+=1
                    self.mcc_table [category_detected][1]+=1
                    if category_expected == category_detected:
                        self.mcc_table[category_detected][2]+=1  
        metric = Metric()
        metric.typical_classification_metrics(self.categories,self.confusion_matrix)
        metric.metric_multiclass_mcc(self.mcc_table)