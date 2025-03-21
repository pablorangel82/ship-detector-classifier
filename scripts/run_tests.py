import unit_tests
import logging
import unit_tests.camera_test
import math

logging.basicConfig(level=logging.INFO, format='%(message)s', )

# unit_tests.camera_test.test_focal_lengh_calculation(10000, [1028, 315, 625, 107])
# unit_tests.camera_test.test_focal_lengh_calculation(20000, [1028, 315, 625, 214])
#iou=unit_tests.camera_test.calculate_iou( [200, 320, 1050, 325], [1028, 315, 1625, 1107])
#print(str(iou))

#unit_tests.camera_test.test_polar_to_ptz()

unit_tests.camera_test.camera.calculate_new_focal_length(0)
# print(math.degrees(unit_tests.camera_test.camera.hfov))
# print(math.degrees(unit_tests.camera_test.camera.vfov))
print(unit_tests.camera_test.camera.focal_length_mm)
print(unit_tests.camera_test.camera.focal_length_px)
