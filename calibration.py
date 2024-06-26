class Calibration:

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
        self.detection_interval = calibration_data['detection_interval']
        self.classification_interval = calibration_data['classification_interval']