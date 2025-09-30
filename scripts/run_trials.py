import logging
from evaluation.tmm_evaluation import TMMEvaluation
from evaluation.dcm_evaluation import DCMEvaluation

logging.basicConfig(level=logging.INFO, format='%(message)s', )

def compute_metrics_tmm(category, test_case):
    tmm_eval = TMMEvaluation(category,test_case)
    tmm_eval.evaluate()

def compute_metrics_dcm():
    dcm_eval = DCMEvaluation()
    dcm_eval.evaluate()

if __name__ == "__main__":
    logging.info("Evaluating DCM... ")
    #compute_metrics_dcm()

    logging.info("Evaluating TMM... ")

    #compute_metrics_tmm(2, '01')
    #compute_metrics_tmm(2, '02')
    #compute_metrics_tmm(20, '03')
    #compute_metrics_tmm(0, '04')
    #compute_metrics_tmm(5, '05')
    compute_metrics_tmm(5, '06')

