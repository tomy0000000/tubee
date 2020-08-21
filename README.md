# Tubee

![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg?logo=python)
[![Travis Build Status](https://img.shields.io/travis/com/tomy0000000/Tubee?logo=Travis)](https://travis-ci.com/tomy0000000/Tubee)
[![codecov](https://codecov.io/gh/tomy0000000/Tubee/branch/master/graph/badge.svg?token=j6pUVAg2Wf)](https://codecov.io/gh/tomy0000000/Tubee)
[![liscense](https://img.shields.io/github/license/tomy0000000/Tubee.svg)](https://github.com/tomy0000000/Tubee/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


<p align="center">
    <img src="tubee/static/favicon.png" align="center">
    <br>
    <img width="150" src="tubee/static/img/tubee_text.png" align="center">
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

- Python 3.5+
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
	--file docker-compose.yml \
	--file docker-compose.dev.yml \
	up --detach --build
```

- Run Migration

```bash
docker-compose \
	--file docker-compose.yml \
	--file docker-compose.dev.yml \
	exec tubee flask deploy
```

### Accessing appication and backends

| Service  | Endpoint                                    |
| -------- | ------------------------------------------- |
| Postgres | postgres://tubee:tubee@localhost:5432/tubee |
| Redis    | redis://localhost:6379                      |
| Flask    | http://localhost:5000                       |

### Build Image for release

```bash
docker build --tag tomy0000000/tubee .
```

## Deployment Guide

- Start Containers

```bash
docker-compose \
	--file docker-compose.yml \
	--file docker-compose.prod.yml \
	up --detach
```

- Run Migration

```bash
docker-compose \
	--file docker-compose.yml \
	--file docker-compose.prod.yml \
	exec tubee flask deploy
```

### Accessing

| Service | Endpoint            |
| ------- | ------------------- |
| Nginx   | http://localhost:80 |

## Maintenance Guide

### Gracefully Restart Nginx

```bash
docker-compose \
	--file docker-compose.yml \
	--file docker-compose.prod.yml \
	kill -s HUP nginx
```

### Gracefully Restart Gunicorn

```bash
docker-compose \
	--file docker-compose.yml \
	--file docker-compose.prod.yml \
	kill -s HUP tubee
```

### Remove Postgres Data

```bash
docker volume rm tubee_postgres_data
```

### Apply Upgrade

```bash
docker build --tag tomy0000000/tubee .
docker-compose \
	--file docker-compose.yml \
	--file docker-compose.prod.yml \
	up --detach --no-deps tubee
```
