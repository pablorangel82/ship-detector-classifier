from core.category import Category
from evaluation.kem_evaluation import KEMEvaluation
from evaluation.dcm_evaluation import DCMEvaluation
from preparation.dataset_config import DatasetConfig
import math
import numpy as np
import os
import logging

class Metric:

    INTERVAL = 0.03

    def show_detection_and_classification_metrics(self):
        tps = []
        tns = []
        fps = []
        fns = []
        dim = len(self.confusion_matrix[0])
        logging.info('\nSummary Table')
        logging.info(self.mcc_table)
        for i in range(dim):
            tp = 0
            for j in range(dim):
                if i == j:
                    tps.append(self.confusion_matrix[i][j])
                    tnsc = 0
                    for k in range(dim):
                        for l in range(dim):
                            if k != i and l != j:
                                tnsc += self.confusion_matrix[k][l]
                    tns.append(tnsc)
                    fnsc = 0
                    for k in range(dim):
                        if k != i:
                            fnsc += self.confusion_matrix[i][k]
                    fns.append(fnsc)
                    fpsc = 0
                    for k in range(dim):
                        if k != j:
                            fpsc += self.confusion_matrix[k][j]
                    fps.append(fpsc)
        logging.info("\nConfusion Matrix")
        logging.info(self.confusion_matrix)
        logging.info('\nDetection and Classification Results')
        for i in range(dim):
            acc = self.metric_acc(tps[i], fps[i], fns[i], tns[i])
            acc = round(acc * 100,2)
            precision = self.metric_precision(tps[i], fps[i])
            precision = round(precision * 100, 2)
            recall = self.metric_true_positive_rate(tps[i], fns[i])
            recall = round(recall * 100, 2)
            f1 = self.metric_f1(precision, recall)
            f1 = round(f1, 2)

            logging.info('\nClass ' + str(i))
            logging.info('\nTrue Positives: ' + str(tps[i]))
            logging.info('\nTrue Negatives: ' + str(tns[i]))
            logging.info('\nFalse Positives: ' + str(fps[i]))
            logging.info('\nFalse Negatives: ' + str(fns[i]))
            logging.info('\nAccuracy: ' + str(acc))
            logging.info('\nPrecision: ' + str(precision))
            logging.info('\nRecall: ' + str(recall))
            logging.info('\nF1 Score: ' + str(f1))

        total_tp = self.sum_vector(tps)
        total_fp = self.sum_vector(fps)
        total_fn = self.sum_vector(fns)
        total_tn = self.sum_vector(tns)

        logging.info('\nOverall metrics')
        acc= self.metric_acc(total_tp, total_fp, total_fn, total_tn)
        acc = round(acc * 100, 2)
        logging.info('Accuracy: ' + str(acc))

        precision = self.metric_precision(total_tp, total_fp)
        precision = round(precision * 100, 2)
        logging.info('Precision:' + str(precision))

        recall = self.metric_true_positive_rate(total_tp, total_fn)
        recall = round(recall * 100, 2)
        logging.info('Recall: ' + str(recall))

        f1 = self.metric_f1(precision, recall)
        f1 = round(f1, 2)
        logging.info('F1 Score:' + str(f1) )

        mcc = round (self.metric_mcc(self.mcc_table),2)
        logging.info('MCC:' + str(mcc) )

    def show_estimation_metrics(self):    
        logging.info('\nMSE Evaluations:')
        for eval in self.kem_evaluations:
            logging.info('\n MSE - Position and Velocity of ' + str(eval.category))
            for key,values in eval.mse_overall_results.items():
                logging.info('UUID: ' + key)
                for reg in values:
                    logging.info('\n Timestamp: ' + str(reg[0]))
                    estimated_lat, estimated_lon, estimated_speed, estimated_course = reg[1]
                    gt_lat, gt_lon, gt_speed, gt_course = reg[2]
                    logging.info('Est: ' + str(estimated_lat) + ', ' + str(estimated_lon))
                    logging.info('GT: ' + str(gt_lat) + ', ' + str(gt_lon))
                    logging.info('Est. Speed: ' + str(estimated_speed) + ' ' + 'Course: ' + str(estimated_course))
                    logging.info('GT. Speed: ' + str(gt_speed) + ' ' + 'Course: ' + str(gt_course))
                    logging.info('\n RMSE Position: ' + str(reg[3]))
                    logging.info('\n RMSE Velocity: ' + str(reg[4]))

    def compute_metrics_dcm(self):
        versions = ['v1','v2','v3']
        list_versions_categories = []
        list_versions_categories.append(Category.load_categories(versions[0],'en'))
        #list_versions_categories.append(self.load_categories(versions[1],'en'))
        #list_versions_categories.append(self.load_categories(versions[2],'en'))
        for k in range(len(list_versions_categories)):
            logging.info('Testing DCM for dataset version ' + str(k+1))
            categories = list_versions_categories[k]
            self.confusion_matrix = np.zeros((len(categories)-1,len(categories)-1), dtype=np.int64) 
            self.mcc_table  = np.zeros((len(categories),3), dtype=np.int64)
            test_images_path = os.path.join(DatasetConfig.DATASET_FOLDER,"test/images")
            test_labels_path = os.path.join(DatasetConfig.DATASET_FOLDER,"test/labels_"+versions[k])
            logging.info('Preparing model... ')
            dcm_eval = DCMEvaluation(self.confusion_matrix,self.mcc_table)
            logging.info("Evaluating DCM... ")
            dcm_eval.evaluate(test_images_path,test_labels_path,versions[k])
            logging.info('Showing metrics...')
            self.show_detection_and_classification_metrics()

    def compute_metrics_kem(self):
        versions = ['v1','v2','v3']
        list_versions_categories = []
        list_versions_categories.append(Category.load_categories(versions[0],'en'))
        # list_versions_categories.append(self.load_categories(versions[1],'en'))
        # list_versions_categories.append(self.load_categories(versions[2],'en'))
        
        
        for k in range(len(list_versions_categories)):
            logging.info('Testing KEM for dataset version ' + str(k+1))
            categories = list_versions_categories[k]
            self.confusion_matrix = np.zeros((len(categories),len(categories)), dtype=np.int64) 
            self.mcc_table  = np.zeros((len(categories),3), dtype=np.int64)
            self.kem_evaluations = []
            for cat in categories:
                cat_id = categories[cat].id
                if cat_id != 3: #provisorio
                    continue
                logging.info('Preparing model for testing category ' + str(cat_id))
                kem_eval = KEMEvaluation(cat_id, self.confusion_matrix, self.mcc_table, Metric.INTERVAL)
                self.kem_evaluations.append(kem_eval)
                i=0
                for i in range(1):
                    logging.info('Evaluating category ' + str(cat_id) + ' with test case ' + str(i))
                    trial = 'evaluation/trials/'+str(cat_id)+"_"+str(i)+'/config'
                    kem_eval.add_test_case(i)
                    logging.info("Evaluating KEM... ")
                    kem_eval.evaluate(i,trial,versions[k])
            logging.info('Showing metrics...')
           # self.show_detection_and_classification_metrics()
            self.show_estimation_metrics()    

    def true_negative_rate(self, tn, fp):
        if (tn + fp) == 0:
            return 0
        return tn / (tn + fp)


    def metric_acc(self, tp, fp, fn, tn):
        if (tp + fn + fp + tn) == 0:
            return 0
        return (tp + tn) / (tp + fn + fp + tn)


    def metric_f1(self, precision, recall):
        if (precision + recall) == 0:
            return 0
        return 2 * ((precision * recall) / (precision + recall))


    def metric_precision(self, tp, fp):
        if (tp + fp) == 0:
            return 0
        return tp / (tp + fp)

    def metric_true_positive_rate(self, tp, fn):
        if (tp + fn) == 0:
            return 0
        return tp / (tp + fn)


    def metric_false_positive_rate(self, fp, tn):
        if (fp + tn) == 0:
            return 0
        return fp / (fp + tn)


    def sum_vector(self,v):
        s = 0
        for i in range(len(v)):
            s = s + v[i]
        return s


    def sum(self,v, col):
        s = 0
        for i in range(len(v)):
            s = s + v[i][col]
        return s


    def sum_prod(self,table, col1, col2):
        s = 0
        for i in range(len(table)):
            s = s + (table[i][col1] * table[i][col2])
        return s


    def metric_mcc(self,table):
        s = self.sum(table, 0)
        c = self.sum(table, 2)
        tp = self.sum_prod(table, 0, 1)
        num = (s * c) - tp
        s2 = s * s
        p2 = self.sum_prod(table, 1, 1)
        t2 = self.sum_prod(table, 0, 0)
        w = (s2 - p2)
        z = (s2 - t2)
        den = math.sqrt(w) * math.sqrt(z)
        if den == 0:
            return -1
        mcc = num / den
        return mcc      