import base64
import json
import threading
import logging
import cv2
from flask import Response
from flask import Flask
from flask import render_template

lock = threading.Semaphore(1)
app = Flask(__name__)
resp_json = ''
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def run():
    t = threading.Thread(target=web)
    t.daemon = True
    t.start()


def web():
    app.run(host='127.0.0.1', port=8000, debug=False, threaded=True, use_reloader=False)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    global resp_json
    with lock:
        jsonString = json.dumps(resp_json)
    response = Response(jsonString, mimetype='"application/json"')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def generate(frame, tracks_list):
    global resp_json
    (flag, encodedImage) = cv2.imencode(".jpg", frame)
    if not flag:
        return None

    tracks = []
    if tracks_list is not None:
        for track in tracks_list.values():
            tracks.append(track.to_json())

    with lock:
        resp_json = {
            'frame': base64.encodebytes(encodedImage).decode('utf-8'),
            'tracks': tracks
        }
