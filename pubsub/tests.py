"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import json

from django.contrib.auth.models import User

from ..users.tests import BaseUserTest

from mynews.users.models import Playlist
from mynews.pubsub.models import Message
from .utils import publish_new_story


class NewStorySignalTest(BaseUserTest):
    def setUp(self, *args, **kwargs):
        super(NewStorySignalTest, self).setUp()
        self.verbose_debugging = True

        # The db instance or our test user
        user = User.objects.get(email=self.username)

        # A test source uri which will receive a new story from sourceproxies
        test_source_uri = "{0}{1}".format(
            "https://sourceproxies.firepl.ug",
            "/sources/feed/aHR0cDovL3BhbmRvZGFpbHkuY29tL2ZlZWQv"
        )

        # Create a playlist that contains our test source
        self.test_playlist, created = Playlist.objects.update_or_create(
            user,
            "test_playlist",
            [test_source_uri]
        )

        story = {
            "source": {
                "url": test_source_uri
            }
        }

        publish_new_story(story)

        self.user_messages = Message.objects.filter(user=user).all()

    def test_new_story_message_present(self):
        message_types = [
            msg.as_dict()["signal_type"]
            for msg
            in self.user_messages
        ]

        self.assertIn(
            "new_story",
            message_types,
            "looking for new story message found {0}".format(
                ",".join(
                    [
                        json.dumps(message.as_dict())
                        for message
                        in self.user_messages
                    ]
                )
            )
        )

    def test_correct_playlists(self):
        message_playlists = [
            msg.as_dict()["params"]["playlist_ids"][0]
            for msg
            in self.user_messages
        ]

        self.assertIn(
            self.test_playlist.pk,
            message_playlists,
            "Playlist id {0} should be in the msg only found {1}".format(
                self.test_playlist.pk,
                ",".join(str(message_playlists))
            )
        )
