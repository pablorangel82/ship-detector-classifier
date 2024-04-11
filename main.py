import math

import cv2
import filters
import samples
from camera import Camera
from detection_management import DetectionManagement

thres = 0.42  # Threshold to detect object
thres_detection = 0.6  # Threshold to detect a vessel
thres_classifier = 0.6  # Threshold to classify a vessel

filepath = samples.load_sample('militar')
categories_filename = 'classifier/ship_types-ptbr'

cap = cv2.VideoCapture(filepath)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

detector = 'detector/detector.pb'
configDetector = 'detector/detector.pbtxt'
classifier = 'classifier/model.pb'

detection_management = DetectionManagement(thres_classifier, categories_filename)
detection_management.start()

netDetector = cv2.dnn_DetectionModel(detector, configDetector)
# netDetector.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
# netDetector.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
netDetector.setInputSize(320, 320)
netDetector.setInputScale(1.0 / 127.5)
netDetector.setInputMean((127.5, 127.5, 127.5))
netDetector.setInputSwapRB(True)
netClassifier = cv2.dnn.readNetFromTensorflow(classifier)
# netClassifier.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
# netClassifier.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

while True:
    success, img = cap.read()
    img_to_show = img.copy()
    classIds, confs, bbox = netDetector.detect(img_to_show, confThreshold=thres)

    if len(classIds) != 0:

        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):

            if classId == 9 and confidence > thres_detection:

                x = box[0]
                y = box[1]
                w = box[2]
                h = box[3]

                x = x - int(w * 0.2)
                y = y - int(h * 0.2)
                size_w = int(w * 1.5)
                size_h = int(h * 1.5)

                if x < 0:
                    x = 0
                if y < 0:
                    y = 0

                vessel_img = img[y:y + size_h, x:x + size_w]
                vessel_img, w, h = filters.transform(vessel_img, size_w, size_h)
                new_img = cv2.normalize(vessel_img, None, 0, 0.2, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
                # cv2.imshow('Ship Detector', vessel_img)
                netClassifier.setInput(cv2.dnn.blobFromImage(new_img, size=(filters.crop_max, filters.crop_max), swapRB=True, crop=False))
                preds = netClassifier.forward()

                track = detection_management.update_track(preds, [x, y, size_w, size_h])

                cv2.rectangle(img_to_show, track.bbox, color=(0, 0, 255), thickness=1)
                name = track.uuid[len(track.uuid)-3]+ track.uuid[len(track.uuid)-2]+ track.uuid[len(track.uuid)-1]
                cv2.putText(img_to_show, track.category.upper() + '(' + str(round(track.confidence * 100)) + ') - ' + name, (x - 10, y - 10),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1)
    cv2.imshow('Ship Detector', img_to_show)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
