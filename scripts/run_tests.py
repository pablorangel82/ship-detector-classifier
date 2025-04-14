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

#unit_tests.camera_test.test_tilt(45,0)
#unit_tests.camera_test.test_tilt(45,1600)
# unit_tests.camera_test.test_tilt(45,1000)
# unit_tests.camera_test.test_tilt(45,8000)

ConverterTest = unit_tests.converter_test.ConverterTest()
logging.info('Verifying if the convertion method (xy to polar) is correct.')
ConverterTest.cases_xy_to_polar()
logging.info('Verifying if the convertion method from (polar to xy) is correct.')
ConverterTest.cases_polar_to_xy()

camera_test = unit_tests.camera_test.CameraTest()
logging.info('Verifying if the pan estimation is correct.')
camera_test.test_pan()
logging.info('Verifying if the tilt estimation is correct.')
camera_test.test_tilt()