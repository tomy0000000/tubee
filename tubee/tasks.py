"""Defines All Async Task for Celery"""
import logging

from . import celery

from .models import Channel

task_logger = logging.getLogger("tubee.task")


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
            task_logger.warning(f"<{channel_id}> Channel not found, skipped.")
            continue
        results[channel_id] = {
            "subscription": channel.subscribe(callback_url, topic_url),
            "info": channel.update_youtube_infos(),
        }
        task_logger.info(f"<{channel_id}> subscription renewed")
        task_logger.info(f"<{channel_id}> information updated")
    channels_update_hub_infos.apply_async(args=[channel_ids_with_url], countdown=60)
    if next_countdown > 0:
        renew_channels.apply_async(
            args=[channel_ids_with_url, next_countdown], countdown=next_countdown
        )
    return results


@celery.task
def channels_update_hub_infos(channel_ids_with_url):
    results = {}
    for channel_id, callback_url, topic_url in channel_ids_with_url:
        channel = Channel.query.get(channel_id)
        if not channel:
            task_logger.warning(f"<{channel_id}> ID not found, skipped.")
            continue
        results[channel_id] = channel.update_hub_infos(callback_url, topic_url)
        task_logger.info(
            f"<{channel_id}> new hub state: {results[channel_id]['state']}"
        )
    return results


@celery.task
def channels_fetch_videos(channel_ids):
    results = {}
    for channel_id in channel_ids:
        channel = Channel.query.get(channel_id)
        if not channel:
            task_logger.warning(f"<{channel_id}> ID not found, skipped.")
            continue
        results[channel_id] = channel.fetch_videos()
        task_logger.info(f"<{channel_id}> videos fetched: {len(results[channel_id])}")
    return results
