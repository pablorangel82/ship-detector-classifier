import unit_tests
import logging
import unit_tests.camera_test

logging.basicConfig(level=logging.INFO, format='%(message)s', )

# unit_tests.camera_test.test_focal_lengh_calculation(10000, [1028, 315, 625, 107])
# unit_tests.camera_test.test_focal_lengh_calculation(20000, [1028, 315, 625, 214])
#iou=unit_tests.camera_test.calculate_iou( [200, 320, 1050, 325], [1028, 315, 1625, 1107])
#print(str(iou))

unit_tests.camera_test.test_polar_to_ptz()