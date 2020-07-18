# Tubee

![Python Version](https://img.shields.io/badge/python-3.5+-blue.svg)
[![Build Status](https://travis-ci.com/tomy0000000/Tubee.svg?token=pcX4zcaLzopbPNP4Hs2J&branch=master)](https://travis-ci.com/tomy0000000/Tubee)
[![codecov](https://codecov.io/gh/tomy0000000/Tubee/branch/master/graph/badge.svg?token=j6pUVAg2Wf)](https://codecov.io/gh/tomy0000000/Tubee)
[![liscense](https://img.shields.io/github/license/tomy0000000/Tubee.svg)](https://github.com/tomy0000000/Tubee/blob/master/LICENSE)

<p align="center">
    <img src="tubee/static/favicon.png" align="center">
    <br>
    <img width="150" src="tubee/static/img/tubee_text.png" align="center">
</p>

## Overview

Tubee is a web application, which runs tasks when your subscribed channel upload new videos.

This application is still in development stage right now, use at your own risk.

## Features

* Push Notification of New Video with
  * [Pushover](https://pushover.net)
  * [LINE Notify](https://notify-bot.line.me)
* Add New Video to Playlist
* Download New Video to Dropbox

## Requirement

* Python 3.5+
* A Web server along with a WSGI server / proxy
  * see [this guide](./deploy/README.md) for more
* A SQL database supported by [SQLAlchemy](https://docs.sqlalchemy.org/en/13/dialects/), PostgresSQL is recommanded
  Be aware this appplication implement some modern modal such as Enum and Json, some database or older version of database might not be compatible.
* [YouTube Data API](https://developers.google.com/youtube/registering_an_application) authorization credentials in **Both**
  * OAuth 2.0 token: used for accessing user information
  * API Keys: used for querying public metadata

For additional operation, you might also need

* [Pushover](https://pushover.net/) API Token
* [Line Notify](https://notify-bot.line.me/zh_TW/) Client ID / Client Secret
* [Dropbox](https://www.dropbox.com/developers/apps) App Key / App Secret

## Installation

* Create a `.env` Environment Variables sheet in the following format

```python
SECRET_KEY=  # Can be generate by running 'import uuid; print(str(uuid.uuid4()))'
DATABASE_URL=
YOUTUBE_API_CLIENT_SECRET_FILE=  # Filename without path
YOUTUBE_API_DEVELOPER_KEY=
PUSHOVER_TOKEN=
LINENOTIFY_CLIENT_ID=
LINENOTIFY_CLIENT_SECRET=
DROPBOX_APP_KEY=
DROPBOX_APP_SECRET=
```

* Place your YouTube Data API Client Secret File under `instance`

* Setup cron job which automatically send a request to application every 4 days at `/api/channels/cron-renew` to ensure channel subscribing will be renew