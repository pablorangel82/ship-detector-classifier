import math
import logging

class Metric:
    def __init__(self):
        self.tps = []
        self.tns = []
        self.fps = []
        self.fns = []
        self.accs = []
        self.precs = []
        self.recalls= []
        self.f1s = []
        self.total_tp = 0
        self.total_tn = 0
        self.total_fp = 0
        self.total_fn = 0
        self.acc = 0
        self.precision = 0
        self.recall = 0
        self.f1 = 0
        self.mcc = 0

    def typical_classification_metrics(self, categories, confusion_matrix):
        self.tps.clear()
        self.tns.clear()
        self.fps.clear()
        self.fns.clear()
        self.accs.clear()
        self.precs.clear()
        self.recalls.clear()
        self.total_tp = 0
        self.total_tn = 0
        self.total_fp = 0
        self.total_fn = 0
        self.acc = 0
        self.precision = 0
        self.recall = 0
        self.f1 = 0
        self.mcc = 0
        dim = len(confusion_matrix[0])
        for i in range(dim):
            tp = 0
            for j in range(dim):
                if i == j:
                    self.tps.append(confusion_matrix[i][j])
                    tnsc = 0
                    for k in range(dim):
                        for l in range(dim):
                            if k != i and l != j:
                                tnsc += confusion_matrix[k][l]
                    self.tns.append(tnsc)
                    fnsc = 0
                    for k in range(dim):
                        if k != i:
                            fnsc += confusion_matrix[i][k]
                    self.fns.append(fnsc)
                    fpsc = 0
                    for k in range(dim):
                        if k != j:
                            fpsc += confusion_matrix[k][j]
                    self.fps.append(fpsc)
        
        
        
        for i in range(dim):
            acc = self.metric_acc(self.tps[i], self.fps[i], self.fns[i], self.tns[i])
            self.accs.append (round(acc * 100,2))
            precision = self.metric_precision(self.tps[i], self.fps[i])
            self.precs.append(round(precision * 100, 2))
            recall = self.metric_true_positive_rate(self.tps[i], self.fns[i])
            self.recalls.append(round(recall * 100, 2))
            f1 = self.metric_f1(precision, recall)
            self.f1s.append(round(f1*100, 2))
            
            result = categories[i].name + ' & ' +  str(acc) + ' & ' +  str(precision) + ' & ' +  str(recall) + ' & ' +  str(f1) + ' \\\\'
           #logging.info(result)

        total_tp = self.sum_vector(self.tps)
        total_fp = self.sum_vector(self.fps)
        total_fn = self.sum_vector(self.fns)
        total_tn = self.sum_vector(self.tns)

        acc= self.metric_acc(total_tp, total_fp, total_fn, total_tn)
        self.acc = round(acc * 100, 2)
        precision = self.metric_precision(total_tp, total_fp)
        self.precision = round(precision * 100, 2)
        recall = self.metric_true_positive_rate(total_tp, total_fn)
        self.recall = round(recall * 100, 2)
        f1 = self.metric_f1(precision, recall)
        self.f1 = round(f1*100, 2)


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

    def metric_binary_mcc(self,tp, tn, fp, fn):
        num = tp * tn - fp * fn
        den = int((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))
        if den <= 0:
            return -1
        den = math.sqrt(den)
        mcc = num/den
        self.mcc = round(mcc,2)
        return mcc

    def metric_multiclass_mcc(self,table):
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
        self.mcc = round (mcc,2)
        return mcc      
    
    def values_bellow_percentile(self, data, p):
        if not data:
            return []
        
        data_sorted = sorted(data)
        n = len(data_sorted)
        rank = p / 100 * (n - 1)
        lower = int(rank)
        upper = min(lower + 1, n - 1)
        weight = rank - lower
        threshold = data_sorted[lower] * (1 - weight) + data_sorted[upper] * weight

        return [x for x in data if x < threshold]
    
    def rmse(self,list):
        if list is None or len(list) == 0:
            return 0
        sum = 0
        for value in list:
            sum+=value
        return sum/len(list)
    
    def med(self,list):
        med = 0
        if len(list) % 2 == 1:
            med = list [int(len(list)/2)]
        else:
            med = (list [(int(len(list)/2))+1] + list [int(len(list)/2)]) /2   
        return math.sqrt(med)