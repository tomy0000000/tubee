import logging
from . import celery
from .models import Channel


@celery.task(bind=True)
def renew_channels(self, channels):
    response = {}
    for index, (channel_id, callback_url, topic_url) in enumerate(channels):
        self.update_state(
            state="PROGRESS",
            meta={
                "current": index + 1,
                "total": len(channels),
                "channel_id": channel_id,
            },
        )
        channel = Channel.query.get(channel_id)
        if not channel:
            continue
        response[channel_id] = {
            "subscription": channel.subscribe(callback_url, topic_url),
            "info": channel.update_infos(),
        }
    channels_update_hub_infos.apply_async(args=[channels], countdown=60)
    logging.info(response)
    return response


@celery.task
def channels_update_hub_infos(channels):
    response = {}
    for channel_id, callback_url, topic_url in channels:
        channel = Channel.query.get(channel_id)
        if not channel:
            continue
        response[channel_id] = channel.update_hub_infos(callback_url, topic_url)
    logging.info(response)
    return response


@celery.task
def channels_fetch_videos(channels):
    response = {}
    for channel_id in channels:
        channel = Channel.query.get(channel_id)
        if not channel:
            continue
        response[channel_id] = channel.fetch_videos()
    logging.info(response)
    return response
