import math

import cv2
import filters
import samples
from detection_management import DetectionManagement

thres = 0.42  # Threshold to detect object
thres_detection = 0.7  # Threshold to detect a vessel
monitor_resolution = (800, 600)

filepath = samples.load_sample('barca1')

cap = cv2.VideoCapture(filepath)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

detector = 'detector/detector.pb'
configDetector = 'detector/detector.pbtxt'
classifier = 'classifier/model.pb'

detection_management = DetectionManagement('en', 'ptbr')
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

                x = x - int (detection_management.pixel_inc_width / 2)
                y = y - int (detection_management.pixel_inc_height / 2)
                size_w = w + detection_management.pixel_inc_width
                size_h = h + detection_management.pixel_inc_height

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
                track = detection_management.update_track(confidence, preds, [x, y, size_w, size_h])
    for track in detection_management.tracks_list:
        cv2.rectangle(img_to_show, track.bbox, color=(0, 0, 255), thickness=2)
        cv2.putText(img_to_show, track.get_description(),
                    (track.bbox[0] - 10, track.bbox[1] - 10),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(img_to_show, 'Position: ' + str(track.lat) + ' - ' + str(track.lon),
                    (track.bbox[0], track.bbox[1]+track.bbox[3] + 30),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)
        cv2.putText(img_to_show, 'Speed: ' + str(track.speed),
                    (track.bbox[0], track.bbox[1] + track.bbox[3] + 90),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)
        cv2.putText(img_to_show, 'Course: ' + str(track.course),
                    (track.bbox[0], track.bbox[1] + track.bbox[3] + 150),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)

    cv2.imshow('Ship Detector', cv2.resize(img_to_show, monitor_resolution))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
