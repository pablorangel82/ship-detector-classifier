import logging

logging.basicConfig(level=logging.INFO, format='%(message)s', )

class Calibration:

    def __init__(self, calibration_data):
        self.threshold_confidence = calibration_data['threshold_confidence']
        self.threshold_iou_detection = calibration_data['threshold_iou_detection']
        self.threshold_iou_tracking = calibration_data['threshold_iou_tracking']
        self.threshold_classification = calibration_data['threshold_classification']
        self.train_image_width = calibration_data['train_img_width']
        self.train_image_height = calibration_data['train_img_height']
        logging.info('\n### Model Calibration Data ###')
        logging.info(f'* IOU for detection: {self.threshold_iou_detection}')
        logging.info(f'* IOU for tracking: {self.threshold_iou_tracking}')
        logging.info(f'* Threshold for detection: {self.threshold_confidence}')
        logging.info(f'* Threshold for classification: {self.threshold_classification}')
        logging.info(f'* Resolution used for trainning: {self.train_image_width,self.train_image_height}')