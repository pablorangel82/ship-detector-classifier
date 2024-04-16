class Calibration:
    pixel_height = 0
    real_height = 0
    real_distance = 0
    threshold_detection = 0
    threshold_detection_vessel = 0
    threshold_classification_vessel = 0
    alpha = 0
    beta = 0
    zoom = 0
    def __init__(self, calibration_data):
        self.pixel_height = calibration_data['pixel_height']
        self.real_height = calibration_data ['real_height']
        self.real_distance = calibration_data['real_distance']
        self.threshold_detection = calibration_data['threshold_detection']
        self.threshold_detection_vessel = calibration_data['threshold_detection_vessel']
        self.threshold_classification_vessel = calibration_data['threshold_classification_vessel']
        self.alpha = calibration_data['alpha']
        self.beta = calibration_data['beta']
        self.zoom = calibration_data['zoom']