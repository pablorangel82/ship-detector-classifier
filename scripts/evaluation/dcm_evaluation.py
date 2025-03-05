from core.dcm import DCM
import logging
import cv2
import codecs
import os

class DCMEvaluation:

    def __init__(self, confusion_matrix, mcc_table):
        self.confusion_matrix = confusion_matrix
        self.mcc_table = mcc_table

    def evaluate(self, test_images_path, test_labels_path, version):
        files = os.listdir(test_images_path)
        dcm = DCM("classification_test", str(version), 'en')
        i=0
        for i in range(len(files)):
            logging.info('Working on file ' + str(i) + ' of ' + str(len(files)))
            each_file = files[i]
            file_name = each_file.split('.')
            src_img_path = os.path.join(test_images_path,each_file)
            src_label_path = os.path.join(test_labels_path,file_name[0]+'.txt')
            img = cv2.imread(src_img_path)
            label = codecs.open(src_label_path, 'r', 'utf-8') 
            lines = label.read()
            category_expected = int(lines.split(' ')[0])
            label.close()
            detection_results = dcm.net_classifier.predict([img],verbose=False,conf=dcm.calibration.threshold_confidence, iou=dcm.calibration.threshold_intersection)
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
                    self.mcc_table [category_expected][1]+=1
                    if category_expected == category_detected:
                        self.mcc_table[category_expected][2]+=1  
