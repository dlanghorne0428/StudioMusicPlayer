# App/consumers.py
"""
Adapted from
https://channels.readthedocs.io/en/latest/tutorial/index.html
"""
# SYNCHRONOUS      
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from App.models.song import Song

import logging
logger = logging.getLogger("django")

class ChatConsumer(WebsocketConsumer):
    # remember the song ID most recently played.
    # don't want to count each message as a play event.
    last_song_id = -1
    
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
        logger.debug(text_data_json)
        
        # if this is a "now_playing message
        if text_data_json["type"] == 'now_playing':
            message = text_data_json["message"]
            logger.debug('message received from websocket')
            message_dict = json.loads(message)
            logger.debug(message_dict)
            
            # increase the play count
            if "song_id" in message_dict:
                song_id_playing = message_dict["song_id"]
                if song_id_playing != self.last_song_id:
                    self.last_song_id = song_id_playing
                    new_song = Song.objects.get(pk=song_id_playing)
                    logger.debug(str(new_song) + ' Plays: ' + str(new_song.num_plays+1))
                    new_song.num_plays += 1
                    new_song.save()
        
            # Send message to group
            async_to_sync(self.channel_layer.group_send)(
                self.group_name, {"type": "now_playing.message", "message": message}
            )
        # if this is a like message
        elif text_data_json["type"] == 'like':
            song_id = text_data_json["song_id"]
            logger.info("User liked song " + song_id)
            song_object = Song.objects.get(pk=song_id)
            song_object.num_likes += 1
            song_object.save()
            
        # if this is an un-like message
        elif text_data_json["type"] == 'unlike':
            song_id = text_data_json["song_id"]
            logger.info("User un-liked song " + song_id)
            song_object = Song.objects.get(pk=song_id)
            song_object.num_likes -= 1
            song_object.save()
                
        # if this is a dislike message
        elif text_data_json["type"] == 'hate':
            song_id = text_data_json["song_id"]
            logger.info("User hated song " + song_id)
            song_object = Song.objects.get(pk=song_id)
            song_object.num_hates += 1
            song_object.save()            

        # if this is a un-dislike message
        elif text_data_json["type"] == 'unhate':
            song_id = text_data_json["song_id"]
            logger.info("User hated song " + song_id)
            song_object = Song.objects.get(pk=song_id)
            song_object.num_hates -= 1
            song_object.save()  

        else:
            logger.warning("Other message type received")

    # Receive message from group
    def now_playing_message(self, event):
        message = event["message"]
        logger.debug(event)
        logger.debug("message received from group")

        #Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))