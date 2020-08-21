"""Defines All Async Task for Celery"""
import logging

from . import celery

# from .helper import build_callback_url, build_topic_url
from .models import Channel


# def schedule_channels_renew(channels, countdown=0):
#     if "GOOGLE_CLOUD_PROJECT_ID" in current_app.config:
#         client, parent = build_cloud_task_service()
#         converted = json.dumps([channel.id for channel in channels]).encode()
#         task = {
#             "app_engine_http_request": {
#                 "http_method": "POST",
#                 "relative_uri": url_for("app_engine.channels_renew"),
#                 "body": converted,
#             }
#         }
#         return client.create_task(parent, task)
#     else:
#         channel_ids_with_url = [
#             (channel.id, build_callback_url(channel.id), build_topic_url(channel.id),)
#             for channel in channels
#         ]
#         return renew_channels.apply_async(args=[channel_ids_with_url], countdown=countdown)


# def schedule_channels_update_hub_infos(channels, countdown=0):
#     if "GOOGLE_CLOUD_PROJECT_ID" in current_app.config:
#         pass
#     else:
#         channel_ids_with_url = [
#             (channel.id, build_callback_url(channel.id), build_topic_url(channel.id),)
#             for channel in channels
#         ]
#         return channels_update_hub_infos.apply_async(
#             args=[channel_ids_with_url], countdown=countdown
#         )


# def schedule_channels_fetch_videos(channels, countdown=0):
#     if "GOOGLE_CLOUD_PROJECT_ID" in current_app.config:
#         pass
#     else:
#         channel_ids_with_url = [
#             (channel.id, build_callback_url(channel.id), build_topic_url(channel.id),)
#             for channel in channels
#         ]
#         return channels_fetch_videos.apply_async(
#             args=[channel_ids_with_url], countdown=countdown
#         )


@celery.task(bind=True)
def renew_channels(self, channel_ids_with_url, next_countdown=-1):
    results = {}
    for index, (channel_id, callback_url, topic_url) in enumerate(channel_ids_with_url):
        self.update_state(
            state="PROGRESS",
            meta={
                "current": index + 1,
                "total": len(channel_ids_with_url),
                "channel_id": channel_id,
            },
        )
        channel = Channel.query.get(channel_id)
        if not channel:
            continue
        results[channel_id] = {
            "subscription": channel.subscribe(callback_url, topic_url),
            "info": channel.update_youtube_infos(),
        }
    channels_update_hub_infos.apply_async(args=[channel_ids_with_url], countdown=60)
    if next_countdown > 0:
        renew_channels.apply_async(
            args=[channel_ids_with_url, next_countdown], countdown=next_countdown
        )
    logging.getLogger("tubee.task").info(results)
    return results


@celery.task
def channels_update_hub_infos(channel_ids_with_url):
    results = {}
    for channel_id, callback_url, topic_url in channel_ids_with_url:
        channel = Channel.query.get(channel_id)
        if not channel:
            continue
        results[channel_id] = channel.update_hub_infos(callback_url, topic_url)
    logging.getLogger("tubee.task").info(results)
    return results


@celery.task
def channels_fetch_videos(channel_ids):
    results = {}
    for channel_id in channel_ids:
        channel = Channel.query.get(channel_id)
        if not channel:
            continue
        results[channel_id] = channel.fetch_videos()
    logging.getLogger("tubee.task").info(results)
    return results
