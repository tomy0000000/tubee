"""Defines All Async Task for Celery"""
import logging

from . import celery

from .models import Channel

task_logger = logging.getLogger("tubee.task")


@celery.task(bind=True)
def renew_channels(self, channel_ids, next_countdown=-1):
    results = {}
    for index, channel_id in enumerate(channel_ids):
        channel = Channel.query.get(channel_id)
        if not channel:
            task_logger.warning(f"<{channel_id}> Channel not found, skipped.")
            continue
        self.update_state(
            state="PROGRESS",
            meta={
                "current": index + 1,
                "total": len(channel_ids),
                "channel_id": channel_id,
                "channel_name": getattr(channel, "name"),
            },
        )
        results[channel_id] = {
            "subscription": channel.subscribe(),
            "info": channel.update(),
        }
        task_logger.info(f"<{channel_id}> subscription renewed")
        task_logger.info(f"<{channel_id}> information updated")
    channels_refresh.apply_async(args=[channel_ids], countdown=60)
    if next_countdown > 0:
        renew_channels.apply_async(
            args=[channel_ids, next_countdown], countdown=next_countdown
        )
    return results


@celery.task
def channels_refresh(channel_ids):
    results = {}
    for channel_id in channel_ids:
        channel = Channel.query.get(channel_id)
        if not channel:
            task_logger.warning(f"<{channel_id}> ID not found, skipped.")
            continue
        results[channel_id] = channel.refresh()
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
