# Tubee

<p align="center">
    <img src="https://raw.githubusercontent.com/tomy0000000/tubee/main/tubee/static/favicon.png">
    <br>
    <img width="150" src="https://raw.githubusercontent.com/tomy0000000/tubee/main/tubee/static/img/tubee_text.png">
    <br>
    <img src="https://img.shields.io/badge/python-3.9-blue.svg?color=brightgreen&logo=python&logoColor=white" alt="Python Version: 3.9" />
    <a href="https://github.com/tomy0000000/tubee/actions/workflows/test.yml">
        <img src="https://img.shields.io/github/workflow/status/tomy0000000/tubee/Test?logo=Github" alt="GitHub Build Status" />
    </a>
    <a href="https://codecov.io/gh/tomy0000000/tubee">
        <img src="https://img.shields.io/codecov/c/github/tomy0000000/tubee?color=brightgreen&logo=codecov&logoColor=white&token=j6pUVAg2Wf" alt="Coverage" />
    </a>
    <br>
    <a href="https://app.fossa.com/projects/git%2Bgithub.com%2Ftomy0000000%2FTubee?ref=badge_shield">
        <img src="https://app.fossa.com/api/projects/git%2Bgithub.com%2Ftomy0000000%2FTubee.svg?type=shield" alt="LICENSE scan status" />
    </a>
    <a href="https://github.com/tomy0000000/Tubee/blob/main/LICENSE">
        <img src="https://img.shields.io/github/license/tomy0000000/Tubee?color=brightgreen" alt="MIT liscense" />
    </a>
    <br>
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
