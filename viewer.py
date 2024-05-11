import copy
import math
import PIL as pil
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import cv2
from numpy import asarray

import detection_management


class Viewer:
    min_width = 600
    max_height_class = 20
    max_height_kinematic = 120

    def __init__(self, monitor_resolution):
        self.hidra_logo = cv2.resize(cv2.imread('viewer/resources/hidra.png', ), (256, 56))
        self.monitor_resolution = monitor_resolution
        self.font_thickness = 2
        self.font_color_not_lost = (0, 153, 255)
        self.font_color_lost = (153, 255, 204)
        self.rectangle_color_not_lost = (0, 0, 0)
        self.rectangle_color_lost = (153, 255, 204)
        self.rectangle_thickness = 2
        self.depth_limit = 7000

    def deg_to_dms(self, deg, type='lat'):
        decimals, number = math.modf(deg)
        d = int(number)
        m = int(decimals * 60)
        s = (deg - d - m / 60) * 3600.00
        compass = {
            'lat': ('N', 'S'),
            'lon': ('E', 'W')
        }
        compass_str = compass[type][0 if d >= 0 else 1]
        return '{}o{}\'{:.2f}"{}'.format(abs(d), abs(m), abs(s), compass_str)

    def draw_logo(self, background, overlay):
        rows_b, cols_b, channels_b = background.shape
        rows_o, cols_o, channels_o = overlay.shape
        rows_b = rows_b - rows_o
        overlay = cv2.addWeighted(background[rows_b:rows_b + rows_o, 0:0 + cols_o], 0.8, overlay, 1, 0)
        background[rows_b:rows_b + rows_o, 0:0 + cols_o] = overlay
        return background

    # def draw_text(self,img, text, pos, dim, bgcolor, lost=False):
    #
    #     color = self.font_color_not_lost
    #     if lost:
    #         color = self.font_color_lost
    #     label = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     pil_image = Image.fromarray(label)
    #     draw = ImageDraw.Draw(pil_image)
    #     size = 28
    #     percent_width = 1
    #     if dim[0] < Viewer.min_width:
    #         percent_width = dim[0] / Viewer.min_width
    #     size = int(size * percent_width)
    #     font = ImageFont.truetype("arial.ttf", size)
    #     if bgcolor is not None:
    #         draw.rectangle([pos[0], pos[1], pos[0] + dim[0], pos[1] + (dim[1]*percent_width)], bgcolor)
    #
    #     for i in range(len(text)):
    #         xy = []
    #         xy.append(0)
    #         xy.append(0)
    #         xy[0]= pos[0] + 10
    #         xy[1]= pos[1] + (i*40*percent_width) + 5
    #         draw.text(xy,text[i], font=font, fill=color)
    #         label = np.asarray(pil_image)
    #         img = cv2.cvtColor(label, cv2.COLOR_RGB2BGR)
    #
    #     return img

    def draw_text(self, img, texts, pos, dim, font_color, rect_color):

        scale = 0.9
        if dim[0] < Viewer.min_width:
            scale = dim[0] / Viewer.min_width

        if scale < 0.5:
            return

        for i in range(len(texts)):
            x = pos[0]
            y = pos[1]
            cv2.rectangle(img, (x, y), (x + dim[0], y + 10 + int(dim[1] * scale)), rect_color, -1)

        for i in range(len(texts)):
            sizes, _ = cv2.getTextSize(texts[i], cv2.FONT_HERSHEY_SIMPLEX, scale, self.font_thickness)
            text_w, text_h = sizes
            x = pos[0] + 2
            y = pos[1] + int (scale * (i * 40) + 5 + text_h)
            cv2.putText(img, texts[i], (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, font_color,
                        self.font_thickness)

    def draw_rectangle(self, image, pos, color):
        cv2.rectangle(image, pos, color=color, thickness=self.rectangle_thickness)

    def show_image(self, img_to_show, tracks_list):
        for track in tracks_list.values():
            if self.depth_limit is not None:
                if track.kinematic.distance_from_camera is not None:
                    if track.kinematic.distance_from_camera > self.depth_limit:
                        continue
            # print(track.to_string())
            lat, lon, speed, course, bbox = track.kinematic.get_current_kinematic()
            name = ''
            if track.get_name() is not None:
                name = track.get_name() + ' - '
            status = track.classification.to_string()
            if track.kinematic.lost:
                status = 'Perdido'
            name_classification = name + status

            font_color = self.font_color_not_lost
            rect_color = self.rectangle_color_not_lost
            if track.kinematic.lost:
                font_color = self.font_color_lost
                rect_color = self.rectangle_color_lost

            self.draw_rectangle(img_to_show, bbox, rect_color)
            self.draw_text(img_to_show, [name_classification], (bbox[0], bbox[1]),
                           (bbox[2], Viewer.max_height_class), font_color, rect_color)
            if lat and lon is not None and status != 'Perdido':
                kinematic = []
                position = 'Posicao:  ' + self.deg_to_dms(lat, 'lat') + ' ' + self.deg_to_dms(lon, 'lon')
                kinematic.append(position)
                dist = round(track.kinematic.distance_from_camera / 1852, 2)
                dist = 'Distancia: ' + str(dist) + ' mn'
                kinematic.append(dist)
                speed_course = 'Calculando rumo e velocidade...'
                if speed is not None:
                    speed_course = 'Velocidade: ' + str(int(speed)) + ' nos' + '     ' + 'Rumo: ' + str(
                        int(course)) + ' graus'
                kinematic.append(speed_course)
                self.draw_text(img_to_show, kinematic, (bbox[0], bbox[1] + bbox[3]),
                               (bbox[2], Viewer.max_height_kinematic), font_color, rect_color)
        img_to_show = self.draw_logo(img_to_show, self.hidra_logo)
        cv2.imshow('Ship Detector', cv2.resize(img_to_show, self.monitor_resolution))

    def quit_command(self, frame_rate):
        if cv2.waitKey(frame_rate) & 0xFF == ord('q'):
            return True
        return False

    def exit(self):
        cv2.destroyAllWindows()
