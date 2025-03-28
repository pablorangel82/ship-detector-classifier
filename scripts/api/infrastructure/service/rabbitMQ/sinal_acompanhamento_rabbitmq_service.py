import pika
import json
import threading
import time

from api.domain.dto.acompanhamento_camera_dto import AcompanhamentoCameraDTO

class SinalACompanhamentoCameraRabbitMQService:
    def __init__(self, config_path):
        json_file = open(config_path + '.json')
        self.config_data = json.load(json_file)
        self.rabbitmq_data = self.config_data['rabbitmq']
        self.exchange = 'sinal.acompanhamento'
        self.exchange_type = 'topic'
        self.connection = None
        self.channel = None
        self.last_date = None
        self.lock = threading.Semaphore(1)
        self.tracks_json = []
        self.connect()
        threading.Thread(target=self.send_tracks, daemon=True).start()
        
    def connect(self):
        credentials = pika.PlainCredentials(self.rabbitmq_data['username'], self.rabbitmq_data['password'])
        parameters = pika.ConnectionParameters(self.rabbitmq_data['host'], credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type, durable=True)
    
    def send_tracks(self):
        while True and self.rabbitmq_data['export']:
            with self.lock:
                if self.tracks_json is not None:
                    self.channel.basic_publish(exchange=self.exchange, routing_key='', body=self.tracks_json)
            time.sleep(1)
            
    def convert_list(self, tracks_list):
        if self.rabbitmq_data['export']:
            converted_list = []
            
            for value in tracks_list.values():
                converted_list.append(AcompanhamentoCameraDTO(value))
                
            if bool(converted_list) and converted_list is not None:
                with self.lock:
                    self.tracks_json = json.dumps([ob.to_json() for ob in converted_list])
        
    def close_connection(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()