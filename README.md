# Tubee

<p align="center">
    <img src="tubee/static/favicon.png">
    <br>
    <img width="150" src="tubee/static/img/tubee_text.png">
    <br>
    <img src="https://img.shields.io/badge/python-3.7+-blue.svg?logo=python" alt="Python Version">
    <a href="https://travis-ci.com/tomy0000000/Tubee">
        <img src="https://img.shields.io/travis/com/tomy0000000/Tubee?logo=Travis" alt="Travis Build Status">
    </a>
    <a href="https://codecov.io/gh/tomy0000000/Tubee">
        <img src="https://codecov.io/gh/tomy0000000/Tubee/branch/master/graph/badge.svg?token=j6pUVAg2Wf" alt="codecov">
    </a>
    <a href="https://github.com/tomy0000000/Tubee/blob/master/LICENSE">
        <img src="https://img.shields.io/github/license/tomy0000000/Tubee.svg" alt="liscense">
    </a>
    <a href="https://github.com/psf/black">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
    </a>
    <a href="https://github.com/prettier/prettier">
        <img src="https://img.shields.io/badge/code%20style-prettier-ff69b4.svg" alt="Code style: prettier">
    </a>
</p>

## Overview

Tubee is a web application, which runs tasks when your subscribed channel upload new videos.

This application is still in development stage, use at your own risk.

## Features

- Push Notification of New Video with
  - [Pushover](https://pushover.net)
  - [LINE Notify](https://notify-bot.line.me)
- Add New Video to Playlist
- Download New Video to Dropbox

## Requirements

- Python 3.7+
- [YouTube Data API](https://developers.google.com/youtube/registering_an_application) authorization credentials in **Both**
  - OAuth 2.0 token: used for accessing user information
  - API Keys: used for querying public metadata

For additional operation, you might also need

- [Pushover](https://pushover.net/) API Token
- [Line Notify](https://notify-bot.line.me/zh_TW/) Client ID / Client Secret
- [Dropbox](https://www.dropbox.com/developers/apps) App Key / App Secret

## Development Guide

### Setup

- Start Containers

```bash
docker-compose \
	--file docker-compose.dev.yml \
	up --detach --build
```

- Run Migration

```bash
docker-compose \
	--file docker-compose.dev.yml \
	exec tubee flask deploy
```

### Accessing appication and backends

| Service        | Endpoint                                    |
| -------------- | ------------------------------------------- |
| Postgres       | postgres://tubee:tubee@localhost:5432/tubee |
| RabbitMQ       | ampq://guest@localhost:5672//               |
| RabbitMQ (Web) | http://localhost:15672                      |
| Redis          | redis://localhost:6379                      |
| Flask          | http://localhost:5000                       |

### Build Image for development

```bash
docker build --build-arg INSTALL_DEV=true --tag tomy0000000/tubee .
```

### Build Image for release

```bash
docker build --tag tomy0000000/tubee .
```

## Deployment Guide

- Start Containers

```bash
docker-compose up --detach
```

- Run Migration

```bash
docker-compose exec tubee flask deploy
```

### Accessing

| Service | Endpoint            |
| ------- | ------------------- |
| Nginx   | http://localhost:80 |

## Maintenance Guide

### Gracefully Restart Nginx

```bash
docker-compose kill -s HUP nginx
```

### Gracefully Restart Gunicorn

```bash
docker-compose kill -s HUP tubee
```

### Gracefully Restart Celery

```bash
docker-compose kill -s HUP celery
```

### Remove Postgres Data

```bash
docker volume rm tubee_postgres_data
```

### Apply Upgrade

```bash
docker build --tag tomy0000000/tubee .
docker-compose up --detach --no-deps tubee
```
