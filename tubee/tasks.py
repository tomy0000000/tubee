"""Defines All Async Task for Celery"""
import logging
from datetime import datetime
from enum import Enum
from random import randrange
from uuid import uuid4

from flask import current_app

from . import celery
from .models import Channel

task_logger = logging.getLogger("tubee.task")


class RenewPolicy(Enum):
    NOW = 0
    ONE_DAY_BEFORE_EXPIRE = -1
    RANDOM = -2


@celery.task(bind=True)
def channels_renew(self, channel_ids, next_countdown=-1):
    results = {}
    for index, channel_id in enumerate(channel_ids):
        channel = Channel.query.get(channel_id)
        if not channel:
            task_logger.warning(
                f"Task <renew_channel>: Channel '{channel_id}' not found, skipped."
            )
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
        channels_renew.apply_async(
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


def list_all_tasks():
    worker_scheduled = celery.control.inspect().scheduled()
    if not worker_scheduled:
        return []

    worker_revoked = celery.control.inspect().revoked()
    if worker_revoked:
        revoked_tasks = [task for worker in worker_revoked.values() for task in worker]
    else:
        revoked_tasks = []

    tasks = []
    for worker in worker_scheduled.values():
        for task in worker:
            task["active"] = bool(task["request"]["id"] not in revoked_tasks)
            tasks.append(task)
    return tasks


def remove_all_tasks():
    worker_tasks = celery.control.inspect().scheduled()
    if not worker_tasks:
        return None
    results = {"removed": [], "error": {}}
    for worker in worker_tasks.values():
        for task in worker:
            try:
                task_id = task["request"]["id"]
                celery.control.revoke(task_id)
                results["removed"].append(task)
            except Exception as error:
                current_app.exception()
                results["error"][task_id] = str(error)
    return results


def issue_channel_renewal(channels):
    task = channels_renew.apply_async(args=[[channel.id for channel in channels]])
    return task


def schedule_channel_renewal(channels, policy: RenewPolicy = RenewPolicy.RANDOM):
    response = {}
    for channel in channels:
        countdown = int((channel.renewal - datetime.now()).total_seconds())
        print(type(countdown))
        if RenewPolicy(policy) is RenewPolicy.RANDOM and countdown > 0:
            countdown = randrange(countdown)
        task = channels_renew.apply_async(
            args=[[channel.id], channel.RENEW_INTERVAL],
            countdown=countdown,
            task_id=f"renew_{channel.id}_{str(uuid4())[:8]}",
        )
        response[channel.id] = task.id
    return response
