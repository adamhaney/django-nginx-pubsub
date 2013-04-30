import mynews.users as Users
from mynews.pubsub.models import Channel


def publish_new_story(story):
    source_uri = story["source"]["url"]
    playlist_sources = Users.models.PlaylistSource.objects.filter(source_uri=source_uri)

    sent_messages = []

    for source in playlist_sources.all():
        playlist = source.playlist
        user = playlist.user
        sent_messages.append(
            Channel(user=user).send_new_story(playlist, story)
        )

    return sent_messages
