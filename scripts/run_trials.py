from evaluation.metrics import Metric
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s', )

m = Metric()
m.compute_metrics_kem()
