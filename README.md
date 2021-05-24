# Tubee

<p align="center">
    <img src="tubee/static/favicon.png">
    <br>
    <img width="150" src="tubee/static/img/tubee_text.png">
    <br>
    <img src="https://img.shields.io/badge/python-3.7+-blue.svg?logo=python" alt="Python Version" />
    <a href="https://github.com/tomy0000000/Tubee/actions/workflows/testing.yml">
        <img src="https://img.shields.io/github/workflow/status/tomy0000000/Tubee/Test%20latest?logo=GitHub%20Actions" alt="GitHub Workflow Status" />
    </a>
    <a href="https://travis-ci.com/tomy0000000/Tubee">
        <img src="https://img.shields.io/travis/com/tomy0000000/Tubee?logo=Travis" alt="Travis Build Status" />
    </a>
    <a href="https://codecov.io/gh/tomy0000000/Tubee">
        <img src="https://codecov.io/gh/tomy0000000/Tubee/branch/master/graph/badge.svg?token=j6pUVAg2Wf" alt="codecov" />
    </a>
    <a href="https://app.fossa.com/projects/git%2Bgithub.com%2Ftomy0000000%2FTubee?ref=badge_shield">
        <img src="https://app.fossa.com/api/projects/git%2Bgithub.com%2Ftomy0000000%2FTubee.svg?type=shield" alt="LICENSE scan status" />
    </a>
    <a href="https://github.com/tomy0000000/Tubee/blob/master/LICENSE">
        <img src="https://img.shields.io/github/license/tomy0000000/Tubee.svg" alt="MIT liscense" />
    </a>
    <a href="https://github.com/psf/black">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black" />
    </a>
    <a href="https://pycqa.github.io/isort">
        <img src="https://img.shields.io/badge/imports-isort-1674b1?labelColor=ef8336&style=flat" alt="Imports: isort" />
    </a>
    <a href="https://github.com/prettier/prettier">
        <img src="https://img.shields.io/badge/code%20style-prettier-ff69b4.svg?logo=Prettier" alt="Code style: prettier" />
    </a>
</p>

## Overview

Tubee is a web application, which runs actions when your subscribed channel upload new videos, think of it as a better IFTTT but built specifically for YouTube with many enhancements.

|                                    | Tubee                       | IFTTT                                  |
| :--------------------------------- | --------------------------- | -------------------------------------- |
| Detaction of new channel video     | Push webhook via **WebSub** | Periodically Pulling (delayed trigger) |
| action for multiple channel        | ✅                          | ❌ (one applet for one channel)        |
| multiple action for single channel | ✅                          | ❌ (one applet for one action)         |

This application is, and will be rolling updated, to conform author's all sort of experiments. You're welcome to use it at your own risk, guides are provided in wiki section.

## Features

Actions that may be executed upon new video being published:

- Push Notification via
  - [Pushover](https://pushover.net)
  - [LINE Notify](https://notify-bot.line.me)
- Add to user's YouTube playlist
- Download to linked Dropbox folder

## Requirements

- Python 3.7+
- [YouTube Data API](https://developers.google.com/youtube/registering_an_application) authorization credentials in both
  - OAuth 2.0 token: used for accessing user information
  - API Keys: used for querying public metadata

For additional operation, you might also need

- [Pushover](https://pushover.net/) API Token
- [Line Notify](https://notify-bot.line.me/zh_TW/) Client ID / Client Secret
- [Dropbox](https://www.dropbox.com/developers/apps) App Key / App Secret
