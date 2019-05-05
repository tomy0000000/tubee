# Tubee

![Python Version](https://img.shields.io/badge/python-3.7-blue.svg)
[![Build Status](https://travis-ci.com/tomy0000000/Tubee.svg?token=pcX4zcaLzopbPNP4Hs2J&branch=master)](https://travis-ci.com/tomy0000000/Tubee)
[![codecov](https://codecov.io/gh/tomy0000000/Tubee/branch/master/graph/badge.svg?token=j6pUVAg2Wf)](https://codecov.io/gh/tomy0000000/Tubee)
[![liscense](https://img.shields.io/github/license/tomy0000000/Tubee.svg)](https://github.com/tomy0000000/Tubee/blob/master/LICENSE)
[![heroku](http://img.shields.io/badge/%E2%86%91%20Deploy%20to-Heroku-7056bf.svg)](https://tubee-heroku.herokuapp.com/)

<p align="center">
    <img src="app/static/favicon.png" align="center">
    <br>
    <img width="150" src="app/static/img/tubee_text.png" align="center">
</p>

# Overview

Tubee is a web application, provides dozens of handful features related to YouTube.

The core functions is completly working, yet development stage is still beta right now, please pm if you're facing any issues😘

# Features

* Channel Subscribing
  * New Video Push Notification (via [Pushover](https://pushover.net/))
  * New Video to Playlist

## More on the Way

* Push Notification with LINE Integration
* New Video Auto download (coming soon)
* Channel Inspection (coming soon)
* Audio Streaming




# TODOs
### Config

* Environment Variables
  * `SECRET_KEY`
  * `DATABASE_URL`
  * `REDIS_PASSWORD`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`
  * `YOUTUBE_API_DEVELOPER_KEY`
  * `PUSHOVER_TOKEN`

* Files
  * `instance/client_secret`

### Testing/Deployment

* Travis CI
  * `.travis.yml`

* Heroku
  * `Procfile`

