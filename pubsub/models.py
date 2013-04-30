import json
import hashlib
import uuid

import requests

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models


class Message(models.Model):
    user = models.ForeignKey(User, related_name='pubsub_messages')
    msg = models.TextField()
    uuid = models.CharField(max_length=36, default=uuid.uuid4())
    timestamp = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        json_msg = json.loads(self.msg)
        json_msg["id"] = self.uuid
        return json_msg


class Channel(object):

    def __init__(self, user):
        self.user = user

    def get_url(self):
        return "{0}/{1}".format(
            settings.PUBSUB_BASE_URL,
            self._get_channel_id()
        )

    def _get_channel_id(self):
        return hashlib.md5(self.user.email + self.user.password).hexdigest()

    def _send_message(self, msg):
        requests.post(
            "{0}/pub?id={1}".format(
                settings.PUBSUB_BASE_URL,
                self._get_channel_id()
            ),
            data=msg
        )
        message = Message.objects.create(user=self.user, msg=msg)
        return message

    def _send_signal(self, signal_type, object_data=None, params=None):
        if object_data is None:
            object_data = {}

        if params is None:
            params = {}

        return self._send_message(
            json.dumps(
                {
                    "signal_type": signal_type,
                    "params": params,
                    "data": object_data
                }
            )
        )

    def send_new_playlist(self, playlist):
        return self._send_signal(
            "new_playlist",
            object_data=playlist.as_dict()
        )

    def send_new_playlist_source(self, playlist, source):
        return self._send_signal(
            "new_playlist_source",
            object_data=source.as_dict(),
            params={
                "playlist": playlist.as_dict()
            }
        )

    def send_new_story(self, playlist, story):
        return self._send_signal(
            "new_story",
            object_data=story,
            params={"playlist_ids": [playlist.pk]}
        )
