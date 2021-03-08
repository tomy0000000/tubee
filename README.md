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

Tubee is a web application, which runs actions when your subscribed channel upload new videos, think of it as a better IFTTT but built specifically for YouTube.

This application is, and will be rolling updated, to conform author's all sort of experiments. You're welcome to use it at your own risk, guides are provided in wiki section.

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
