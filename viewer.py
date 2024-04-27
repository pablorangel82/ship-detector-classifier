from PIL import ImageFont, ImageDraw, Image
import numpy as np
import cv2

import detection_management


class Viewer:
    monitor_resolution = (800, 600)
    font = None
    font_thickness = 2
    font_color = (0, 0, 0)
    rectangle_color = (0, 0, 0)
    rectangle_thickness = 2
    depth_limit = None

    def build_label(self, image, text, location):
        label = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(label)

        draw = ImageDraw.Draw(pil_image)
        font = ImageFont.truetype('viewer/resources/Arial.ttf', 24)
        draw.text(location, text, font=font, fill=self.font_color)

        label = np.asarray(pil_image)
        img_with_label = cv2.cvtColor(label, cv2.COLOR_RGB2BGR)

        return img_with_label

    def show_image(self, img_to_show, tracks_list, semaphore):
        with semaphore:
            for track in tracks_list.values():
                if self.depth_limit is not None:
                    if track.kinematic.distance_from_camera is not None:
                        if track.kinematic.distance_from_camera  > self.depth_limit:
                            continue
                # print(track.to_string())
                lat, lon, speed, course, bbox = track.kinematic.get_current_kinematic()
                cv2.rectangle(img_to_show, bbox, color=self.rectangle_color, thickness=self.rectangle_thickness)
                name_classification = track.get_name() + ' - ' + track.classification.to_string()
                img_to_show = self.build_label(img_to_show, name_classification, (bbox[0], bbox[1] - 30))
                if lat and lon and speed and course is not None:
                    position = 'Posição: ' + str(lat) + ', ' + str(lon)
                    dist = round(track.kinematic.distance_from_camera/1852, 2)
                    img_to_show = self.build_label(img_to_show, position,(bbox[0],bbox[1] + bbox[3] + 10))
                    dist = 'Distancia: ' + str(dist) + ' milhas nauticas'
                    img_to_show = self.build_label(img_to_show, dist,(bbox[0],bbox[1] + bbox[3] + 50))
                    speed_course = 'Velocidade: ' + str(int(speed)) + ' nós' + '        ' + 'Rumo: ' + str(int(course)) + ' º'
                    img_to_show = self.build_label(img_to_show, speed_course,(bbox[0], bbox[1] + bbox[3] + 90))
        cv2.imshow('Ship Detector', cv2.resize(img_to_show, self.monitor_resolution))

    def quit_command(self):
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return True
        return False

    def exit(self):
        cv2.destroyAllWindows()
