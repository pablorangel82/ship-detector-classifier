from core.dcm import DCM
import logging
import cv2
import codecs
import os
import numpy as np
from core.category import Category
from preparation.dataset_config import DatasetConfig
from evaluation.metrics import Metric
from ultralytics import YOLO
import pandas as pd
from collections import defaultdict

class DCMEvaluation:

    def __init__(self):
        self.path = '../report/evaluation/trials/dcm/'
        self.test_images_path = os.path.join(DatasetConfig.ORIGINAL_DATASET_FOLDER,"test/images")
        self.test_labels_path = os.path.join(DatasetConfig.ORIGINAL_DATASET_FOLDER,"test/labels")
        self.categories = Category.load_categories('en')
        self.confusion_matrix = np.zeros((len(self.categories)-1,len(self.categories)-1), dtype=np.int64) 
        self.mcc_table  = np.zeros((len(self.categories),3), dtype=np.int64)

    def evaluate(self):
        files = os.listdir(self.test_images_path)
        path_to = os.path.join(self.path,'config')
        dcm = DCM(path_to, 'en')
        i=0
        logging.info('\n')
        for i in range(len(files)):
            if i % 100 == 0 or (len(files) - i) <= 10:
                logging.info('Working on file ' + str(i) + ' of ' + str(len(files)))
            each_file = files[i]
            file_name = each_file.split('.')
            src_img_path = os.path.join(self.test_images_path,each_file)
            src_label_path = os.path.join(self.test_labels_path,file_name[0]+'.txt')
            img = cv2.imread(src_img_path)
            label = codecs.open(src_label_path, 'r', 'utf-8') 
            lines = label.read()
            category_expected = int(float(lines.split(' ')[0]))
            label.close()
            detection_results = dcm.net_classifier.predict([img],imgsz=dcm.calibration.train_image_width,verbose=False,conf=dcm.calibration.threshold_confidence, iou=dcm.calibration.threshold_iou_tracking)
            for result in detection_results:
                for box in result.boxes:
                    confidence = max(box.conf.tolist())
                    index_confidence = box.conf.tolist().index (confidence)
                    category_detected = int(box.cls.tolist()[index_confidence])          
                    self.mcc_table [category_expected][0]+=1
                    self.mcc_table [category_detected][1]+=1
                    self.confusion_matrix[category_expected][category_detected] += 1
                    if category_expected == category_detected:
                        self.mcc_table[category_detected][2]+=1  

        metric = Metric()
        metric.typical_classification_metrics(self.categories,self.confusion_matrix)
        metric.metric_multiclass_mcc(self.mcc_table)
        
        path_to_save = os.path.join(self.path,'dcm_result.latex')   
        tfile = codecs.open(path_to_save, 'w', 'utf-8') 
        tfile.write(metric.results_latex)
        tfile.close()
        logging.info(metric.results_latex)

    def iou(self,boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        inter = max(0, xB - xA) * max(0, yB - yA)
        areaA = max(0, boxA[2] - boxA[0]) * max(0, boxA[3] - boxA[1])
        areaB = max(0, boxB[2] - boxB[0]) * max(0, boxB[3] - boxB[1])
        union = areaA + areaB - inter
        return inter / union if union > 0 else 0

    def safe_div(self, a, b):
        return a / b if b > 0 else 0.0
    
    def evaluate_2(self):
        MODEL_PATH = "core/models/best.pt"
        DATA_PATH = "../report/evaluation/trials/dcm/data.yaml"
        IOU_THRESHOLD = 0.5
        
        model = YOLO(MODEL_PATH)
        
        results = model.val(data=DATA_PATH, device=[0], iou=IOU_THRESHOLD)

        TP, FP, FN, GT_counts = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
        all_classes = set()

        for r in results:
            gt_boxes = r.boxes.gt.xyxy.cpu().numpy() if hasattr(r.boxes, "gt") and r.boxes.gt is not None else []
            gt_classes = r.boxes.gt.cls.cpu().numpy().astype(int) if hasattr(r.boxes, "gt") and r.boxes.gt is not None else []

            pred_boxes = r.boxes.xyxy.cpu().numpy() if r.boxes is not None else []
            pred_classes = r.boxes.cls.cpu().numpy().astype(int) if r.boxes is not None else []

            gt_matched = [False] * len(gt_boxes)

            for pb, pc in zip(pred_boxes, pred_classes):
                all_classes.add(pc)
                best_iou, best_idx = 0, -1
                for i, (gb, gc) in enumerate(zip(gt_boxes, gt_classes)):
                    if gt_matched[i] or gc != pc:
                        continue
                    cur_iou = iou(pb, gb)
                    if cur_iou > best_iou:
                        best_iou, best_idx = cur_iou, i
                if best_iou >= IOU_THRESHOLD and best_idx >= 0:
                    TP[pc] += 1
                    gt_matched[best_idx] = True
                else:
                    FP[pc] += 1

            for i, matched in enumerate(gt_matched):
                if not matched:
                    gcls = gt_classes[i]
                    FN[gcls] += 1
                    all_classes.add(gcls)
                    GT_counts[gcls] += 1

        rows = []
        for cls in sorted(all_classes):
            tp, fp, fn = TP[cls], FP[cls], FN[cls]
            precision = self.safe_div(tp, tp + fp)
            recall = self.safe_div(tp, tp + fn)
            f1 = self.safe_div(2 * precision * recall, precision + recall)
            acc = self.safe_div(tp, tp + fp + fn)
            rows.append({
                "Class": model.names.get(cls, str(cls)),
                "TP": tp, "FP": fp, "FN": fn,
                "Precision": precision,
                "Recall": recall,
                "F1-score": f1,
                "Accuracy": acc
            })

        df = pd.DataFrame(rows)
        print("\Metrics per class (IoU >= {:.2f}):\n".format(IOU_THRESHOLD))
        print(df.to_string(index=False, float_format="%.3f"))

        TP_total, FP_total, FN_total = sum(TP.values()), sum(FP.values()), sum(FN.values())
        prec_micro = self.safe_div(TP_total, TP_total + FP_total)
        rec_micro   = self.safe_div(TP_total, TP_total + FN_total)
        f1_micro    = self.safe_div(2 * prec_micro * rec_micro, prec_micro + rec_micro)
        acc_micro   = self.safe_div(TP_total, TP_total + FP_total + FN_total)

        print("\Agreggated (micro):")
        print(f"Precision = {prec_micro:.3f}")
        print(f"Recall   = {rec_micro:.3f}")
        print(f"F1-score = {f1_micro:.3f}")
        print(f"Accuracy = {acc_micro:.3f}")