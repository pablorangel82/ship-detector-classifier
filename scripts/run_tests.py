import unit_tests
import logging
import unit_tests.camera_test
import unit_tests.converter_test
import math

logging.basicConfig(level=logging.INFO, format='%(message)s', )

#unit_tests.camera_test.test_focal_lengh_calculation(18131.67, [960, 315, 625, 230])
# unit_tests.camera_test.test_focal_lengh_calculation(20000, [1028, 315, 625, 214])
#iou=unit_tests.camera_test.calculate_iou( [200, 320, 1050, 325], [1028, 315, 1625, 1107])
#print(str(iou))

#unit_tests.camera_test.test_polar_to_ptz()

#unit_tests.camera_test.camera.calculate_new_focal_length(1)
# print(math.degrees(unit_tests.camera_test.camera.hfov))
# print(math.degrees(unit_tests.camera_test.camera.vfov))

unit_tests.camera_test.test_tilt(45,0)
unit_tests.camera_test.test_tilt(45,1600)
# unit_tests.camera_test.test_tilt(45,1000)
# unit_tests.camera_test.test_tilt(45,8000)

#unit_tests.converter_test.test_xy_to_polar()
#unit_tests.converter_test.test_polar_to_xy()