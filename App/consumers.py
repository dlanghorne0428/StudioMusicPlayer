# App/consumers.py
"""
Adapted from
https://channels.readthedocs.io/en/latest/tutorial/index.html
"""
# SYNCHRONOUS      
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

import logging
logger = logging.getLogger("django")

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "now_playing"

        # Join group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        logger.debug('message received from websocket')
        
        # Send message to group
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {"type": "now_playing.message", "message": message}
        )

    # Receive message from group
    def now_playing_message(self, event):
        message = event["message"]
        logger.debug(event)
        logger.debug("message received from group")

        #Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))