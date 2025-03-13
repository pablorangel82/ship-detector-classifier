import queue
import cv2
import base64
import json

class ClassificationPublisher(queue.Queue):
    def write(self, frame, tracks):
        if frame is not None and frame.size > 0:
            if not self.empty():
                while not self.empty():
                    self.get_nowait()
            self.put_nowait(f'{self.generate(frame, tracks)}\n\n')

    def __iter__(self):
        return iter(self.get, None)

    def generate(self, frame, tracks_list):
        success, encoded_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not success:
            return None

        tracks = []
        if tracks_list is not None:
            for track in tracks_list.values():
                tracks.append(track.to_json())

        return json.dumps({
            'frame': base64.b64encode(encoded_frame).decode('utf-8'),
            'tracks': tracks
        })