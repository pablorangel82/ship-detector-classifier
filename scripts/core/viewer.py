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

def view (frame, tracks):
    image = frame
    text_values = []
    for track in tracks.values():
        lat, lon, speed, course, bearing, dist, bbox = track.kinematic.get_current_kinematic()
        if lat and lon is not None:
            distance_realibility = False
            unknown_id = (Category.CATEGORIES[len(Category.CATEGORIES) -1]).id
            if track.classification.category.id != unknown_id and speed is not None:
                distance_realibility = True
                speed = float(speed)
                course =float(course)
                dist = round(track.kinematic.distance_from_camera / 1852, 2)
            else:
                speed = None
                course = None
                dist = None
            px= int(bbox[0])
            py= int(bbox[1])
            w= int(bbox[2])
            h= int(bbox[3])
            
            if track.kinematic.lost:
                image = cv2.rectangle(image, (px,py), (px+w,py+h), color_rect_lost,1)
            else:
                text = track.classification.to_string()
                xmin = int(px + (w/4))
                ymin = int(py - (font_size * 4))
                rect_width = (font_size * len(text) * 0.6)+2
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
                ymin = int(py-(font_size*4))
                text_values.append([text,xmin,ymin,color_text_title])
                if distance_realibility == False:
                    ymin = int(py - (font_size * 2))
                    bearing = round(bearing)
                    text = 'Bearing: ' + str(bearing) + ' º';  
                    text_values.append([text,xmin,ymin,color_text_body])
                else:
                    if speed < 2:
                        speed = 0
                        course = '-'
                    else:
                        if speed > 40:
                            speed='-'
                            course='-'
                        else:
                            speed = round(speed)
                            course = round(course)
                    error = ''
                    if track.kinematic.error is not None:
                        error_position, error_velocity = track.kinematic.error
                        error = 'EP: ' + str(error_position) + ' EV: ' + str(error_velocity)
                    
                    text = error
                    ymin = int(py - (font_size * 3))
                    text_values.append([text,xmin,ymin,color_text_body])
                    text = 'Position: ' + deg_to_dms(lat,'lat') + '    ' + deg_to_dms (lon,'lon')
                    ymin = int(py - (font_size * 2))
                    text_values.append([text,xmin,ymin,color_text_body])
                    ymin = int(py - (font_size * 1))
                    text = 'Speed: ' + str(speed) + " KT" + "   Course: " + str(course) + " º" 
                    text_values.append([text,xmin,ymin,color_text_body])
    image = draw_texts(image, text_values)                
    cv2.imshow("Ship Detector Classifier",image)
    
