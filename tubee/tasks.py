"""Defines All Async Task"""
import logging
import json

from flask import current_app, url_for

from . import celery
from .helper import build_callback_url, build_topic_url, build_cloud_task_service
from .models import Channel


def schedule_channels_renew(channels, countdown=0):
    if "GOOGLE_CLOUD_PROJECT_ID" in current_app.config:
        client, parent = build_cloud_task_service()
        converted = json.dumps([channel.id for channel in channels]).encode()
        task = {
            "app_engine_http_request": {
                "http_method": "POST",
                "relative_uri": url_for("app_engine.channels_renew"),
                "body": converted,
            }
        }
        return client.create_task(parent, task)
    else:
        channels_with_urls = []
        for channel in channels:
            channels_with_urls.append(
                (
                    channel.id,
                    build_callback_url(channel.id),
                    build_topic_url(channel.id),
                )
            )
        return renew_channels.apply_async(
            args=[channels_with_urls], countdown=countdown
        )


def schedule_channels_update_hub_infos(channels, countdown=0):
    if "GOOGLE_CLOUD_PROJECT_ID" in current_app.config:
        pass
    else:
        channels_with_urls = []
        for channel in channels:
            channels_with_urls.append(
                (
                    channel.id,
                    build_callback_url(channel.id),
                    build_topic_url(channel.id),
                )
            )
        return channels_update_hub_infos.apply_async(
            args=[channels_with_urls], countdown=countdown
        )


def schedule_channels_fetch_videos(channels, countdown=0):
    if "GOOGLE_CLOUD_PROJECT_ID" in current_app.config:
        pass
    else:
        channels_with_urls = []
        for channel in channels:
            channels_with_urls.append(
                (
                    channel.id,
                    build_callback_url(channel.id),
                    build_topic_url(channel.id),
                )
            )
        return channels_fetch_videos.apply_async(
            args=[channels_with_urls], countdown=countdown
        )


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
