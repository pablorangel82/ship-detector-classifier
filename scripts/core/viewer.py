from core.category import Category
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

color_text_body = (255, 255, 255)
color_text_title = (226, 135, 67)
color_rect_active =  (0, 0, 0)
color_rect_lost = (235,206,135)
color_pin = (67, 135, 226)
min_rect_width = 300
font_size = 12
font_type = ImageFont.truetype("resources/arial.ttf", font_size)
show_bb_active_track = True


def deg_to_dms(deg, coord_type='lat'):
    degrees = int(deg)
    decimals = deg - degrees
    minutes = int(decimals * 60)
    seconds = (decimals * 3600) % 60

    compass = {
        'lat': ['N', 'S'],
        'lon': ['E', 'W']
    }

    compass_str = compass[coord_type][0 if degrees >= 0 else 1]

    return f"{abs(degrees)}º{abs(minutes)}'{abs(seconds):.2f}\"{compass_str}"


def draw_texts(source_image,values): 
    image = cv2.cvtColor(source_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image)

    for text,x,y,color in values:
        draw = ImageDraw.Draw(pil_image)
        draw.text((x, y), text, font=font_type, fill=color)
        
    image = np.asarray(pil_image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image

def view (frame, tracks, camera_bearing, ptz):
    image = frame
    text_values = []
    for track in tracks.values():
        unknown_id = (Category.CATEGORIES[len(Category.CATEGORIES) -1]).id
        lat, lon, speed, course, bearing, dist, bbox = track.get_current_kinematic()
        elected_category = track.classification.elected
        bearing = round(bearing,2)
        if elected_category[0].id != unknown_id:
            dist = round(dist / 1000, 2) #m->km
            speed = round(float(speed))
            course =round(float(course))
            if speed < 2:
                if speed == 0:
                    speed = '-'
                    course = '-'
                else:
                    speed = 0
                    course = '-'
            else:
                if speed > 40:
                    speed='-'
                    course='-'
            text_velociy = 'Speed: ' + str(speed) + " KT" + "   Course: " + str(course) + " º" 
            text_geopos = 'Geo Position: ' + deg_to_dms(lat,'lat') + '    ' + deg_to_dms (lon,'lon')
            text_polar = 'Bearing: ' + str(bearing) + ' º' + '    Distance from camera: ' + str(dist) + ' km'
        else:
            text_velociy = None 
            text_geopos = None 
            text_polar = 'Bearing: ' + str(bearing) + ' º' + '    Distance from camera:-  km'

            
        px= int(bbox[0])
        py= int(bbox[1])
        w= int(bbox[2])
        h= int(bbox[3])
        
        if track.lost:
            image = cv2.rectangle(image, (px,py), (px+w,py+h), color_rect_lost,1)
        else:
            if show_bb_active_track:
                image = cv2.rectangle(image, (px,py), (px+w,py+h), color_rect_active,1)
            text_title = track.classification.to_string()
            xmin = int(px + (w/4))
            ymin = int(py - (font_size * 5))
            rect_width = (font_size * len(text_title) * 0.6)+2
            if rect_width < min_rect_width:
                rect_width = min_rect_width 
            xmax = int(px + rect_width + (w/4))
            ymax = int(py) 
            xcenter_src = int(xmin + (rect_width/2))
            xcenter_dst = int(px + (w/2))
            ycenter = int(py + (h/2))
            image = cv2.rectangle(image, (xmin,ymin), (xmax,ymax), color_rect_active,-1)
            image = cv2.line(image, (xcenter_src,ymax),(xcenter_dst,ycenter),color_rect_active,2 )
            image = cv2.circle(image,(xcenter_dst,ycenter),10,color_pin,-1)
            ymin = int(py-(font_size*5))
            text_values.append([text_title,xmin,ymin,color_text_title])
            ymin = int(py - (font_size * 3))
            text_values.append([text_polar,xmin,ymin,color_text_body])
            if text_geopos is not None:
                ymin = int(py - (font_size * 2))
                text_values.append([text_geopos,xmin,ymin,color_text_body])
            if text_velociy is not None:
                ymin = int(py - (font_size * 1))
                text_values.append([text_velociy,xmin,ymin,color_text_body])

    text_camera_bearing =  str(round(camera_bearing,2))
    text_ptz = 'P: ' + str(round(ptz[0],2)) + ' T: ' + str(round(ptz[1],2)) + ' Z: ' + str(round(ptz[2],2)) 

    text_values.append(['Camera\'s bearing: ' + text_camera_bearing, 10, 10, color_text_body])
    text_values.append(['Camera\'s PTZ: ' + text_ptz, 10, 30, color_text_body])
    
    image = draw_texts(image, text_values)
    

    cv2.imshow("Ship Detector Classifier",image)
    
