class Calibration:

    def __init__(self, calibration_data):
        self.threshold_confidence = calibration_data['threshold_confidence']
        self.threshold_classification = calibration_data['threshold_classification']
        self.threshold_intersection = calibration_data['threshold_intersection']
        self.train_image_width = calibration_data['train_img_width']
        self.train_image_height = calibration_data['train_img_height']
        self.resize = calibration_data['resize']