import math
import logging

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
        self.recalls = []
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
        self.results_latex = ''


    def typical_classification_metrics(self, categories, confusion_matrix):
        self.tps.clear()
        self.tns.clear()
        self.fps.clear()
        self.fns.clear()
        self.accs.clear()
        self.precs.clear()
        self.recalls.clear()
        self.f1s.clear()
        self.total_tp = self.total_tn = self.total_fp = self.total_fn = 0
        self.acc = self.precision = self.recall = self.f1 = self.mcc = 0

        dim = len(confusion_matrix)
        total = sum(sum(row) for row in confusion_matrix)

        for i in range(dim):
            tp = confusion_matrix[i][i]
            fn = sum(confusion_matrix[i]) - tp
            fp = sum(row[i] for row in confusion_matrix) - tp
            tn = total - tp - fp - fn

            self.tps.append(tp)
            self.fns.append(fn)
            self.fps.append(fp)
            self.tns.append(tn)

        for i in range(dim):
            acc = self.metric_accuracy(self.tps[i], self.fps[i], self.fns[i], self.tns[i])
            precision = self.metric_precision(self.tps[i], self.fps[i])
            recall = self.metric_true_positive_rate(self.tps[i], self.fns[i])
            f1 = self.metric_f1(precision, recall)

            self.accs.append(round(acc * 100, 2))
            self.precs.append(round(precision * 100, 2))
            self.recalls.append(round(recall * 100, 2))
            self.f1s.append(round(f1 * 100, 2))

            self.results_latex+=f'\n{categories[i].name} & {acc:.4f} & {precision:.4f} & {recall:.4f} & {f1:.4f} \\\\'

        total_tp = sum(self.tps)
        total_fp = sum(self.fps)
        total_fn = sum(self.fns)
        total_tn = sum(self.tns)

        self.acc = round(self.metric_accuracy(total_tp, total_fp, total_fn, total_tn) * 100, 2)
        self.precision = round(self.metric_precision(total_tp, total_fp) * 100, 2)
        self.recall = round(self.metric_true_positive_rate(total_tp, total_fn) * 100, 2)
        self.f1 = round(self.metric_f1(self.precision / 100, self.recall / 100) * 100, 2)
        self.results_latex+=f'\nGeneral Evaluation: {self.acc:.4f} & {self.precision:.4f} & {self.recall:.4f} & {self.f1:.4f} \\\\'


    def metric_accuracy(self, tp, fp, fn, tn):
        total = tp + fp + fn + tn
        return (tp + tn) / total if total > 0 else 0

    def metric_f1(self, precision, recall):
        return 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    def metric_precision(self, tp, fp):
        return tp / (tp + fp) if (tp + fp) > 0 else 0

    def metric_true_positive_rate(self, tp, fn):
        return tp / (tp + fn) if (tp + fn) > 0 else 0

    def metric_true_negative_rate(self, tn, fp):
        return tn / (tn + fp) if (tn + fp) > 0 else 0

    def metric_false_positive_rate(self, fp, tn):
        return fp / (fp + tn) if (fp + tn) > 0 else 0

    def metric_binary_mcc(self, tp, tn, fp, fn):
        num = tp * tn - fp * fn
        den = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
        if den <= 0:
            return -1
        mcc = num / math.sqrt(den)
        self.mcc = round(mcc, 2)
        return mcc

    def metric_multiclass_mcc(self, table):
        s = self._sum(table, 0)
        c = self._sum(table, 2)
        tp = self._sum_prod(table, 0, 1)
        num = s * c - tp
        s2 = s * s
        p2 = self._sum_prod(table, 1, 1)
        t2 = self._sum_prod(table, 0, 0)
        w = s2 - p2
        z = s2 - t2
        den = math.sqrt(w * z)
        if den == 0:
            return -1
        mcc = num / den
        self.mcc = round(mcc, 2)
        self.results_latex+=f'\nMCC: {self.mcc}'
        return mcc

    def values_below_percentile(self, data, p):
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

    def med(self, data):
        if not data:
            return 0
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 0:
            med = (sorted_data[mid - 1] + sorted_data[mid]) / 2
        else:
            med = sorted_data[mid]
        return math.sqrt(med)

    def _sum(self, matrix, col):
        return sum(row[col] for row in matrix)

    def _sum_prod(self, matrix, col1, col2):
        return sum(row[col1] * row[col2] for row in matrix)
