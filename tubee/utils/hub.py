"""PubSubHubbub Communication Package

Build upon PubSubHubbub 0.4 Specification
https://pubsubhubbub.github.io/PubSubHubbub/pubsubhubbub-core-0.4.html

Using Google Hub at
https://pubsubhubbub.appspot.com

Variables:
    DEFAULT_HEADERS {dict} -- The default header used when sending a request to
                              hub
    REQUIRED_PARAMETERS {list} -- A list of required parameters to compsoe
                                  request to hub
"""

import re
from urllib.parse import urljoin, urlparse

import bs4
import requests

from . import try_parse_datetime

DEFAULT_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
}
REQUIRED_PARAMETERS = ["hub.callback", "hub.mode", "hub.topic"]


class MissingRequiredParameterError(Exception):
    """Raised when a required parameter is missing"""

    def __init__(self, message, parameter):
        super().__init__(message)
        self.parameter = parameter


class NonSecureHubSecretError(Exception):
    """Raised when Hub secret is sending with http callback url"""

    def __init__(self):
        super().__init__("Hub Secret is not allowed when using http")


def _formal_post_request(hub, endpoint, **data):
    """
    Required Parameters:
    hub.callback            Subscribers Endpoint
    hub.mode                subscribe / unsubscribe
    hub.topic               Content of Subcription

    Optional Parameters:
    hub.lease_seconds       Duration of the subscription in seconds
    hub.secret              Subscriber-provided secret string
    """

    # Check Required Parameters
    for param in REQUIRED_PARAMETERS:
        if param not in data:
            message = "Request missing a required field: " + param
            raise MissingRequiredParameterError(message, param)

    # Check hub.secret Validity
    callback_scheme = urlparse(data["hub.callback"]).scheme
    if callback_scheme == "http" and data["hub.secret"]:
        raise NonSecureHubSecretError()

    # Sending Requests
    response = requests.post(
        url=urljoin(hub, endpoint),
        headers=DEFAULT_HEADERS,
        data=data,
    )
    response.raise_for_status()
    return response


def _formal_get_request(hub, endpoint, **params):
    """
    Required Parameters:
    hub.callback            Subscribers Endpoint
    hub.topic               Content of Subcription

    Optional Parameters:
    hub.secret              Subscriber-provided secret string
    """
    response = requests.get(
        url=urljoin(hub, endpoint),
        headers=DEFAULT_HEADERS,
        params=params,
    )
    response.raise_for_status()
    return response


def _parse_detail(query, fuzzy=False):
    parsed_datetime = try_parse_datetime(query)
    if not fuzzy or not parsed_datetime:
        return parsed_datetime
    if summary := re.search(r"\((.*)\)", query):
        summary = summary.groups()[0]
    return (parsed_datetime, summary)


def subscribe(hub_url, callback_url, topic_url, **kwargs):
    """
    Optional Parameters:
    lease_seconds       Duration of the subscription in seconds
    secret              Subscriber-provided secret string
    """
    data = {
        "hub.callback": callback_url,
        "hub.mode": "subscribe",
        "hub.topic": topic_url,
        "hub.lease_seconds": kwargs.get("lease_seconds"),
        "hub.secret": kwargs.get("secret"),
    }
    response = _formal_post_request(hub_url, "subscribe", **data)
    response.success = bool(response.status_code == 202)
    return response


def unsubscribe(hub_url, callback_url, topic_url, **kwargs):
    """
    Optional Parameters:
    lease_seconds       Duration of the subscription in seconds
    secret              Subscriber-provided secret string
    """
    data = {
        "hub.callback": callback_url,
        "hub.mode": "unsubscribe",
        "hub.topic": topic_url,
        "hub.lease_seconds": kwargs.get("lease_seconds"),
        "hub.secret": kwargs.get("secret"),
    }
    response = _formal_post_request(hub_url, "subscribe", **data)
    response.success = bool(response.status_code == 202)
    return response


def details(hub_url, callback_url, topic_url, **kwargs):
    """
    Optional Parameters:
    secret              Subscriber-provided secret string
    """
    params = {
        "hub.callback": callback_url,
        "hub.topic": topic_url,
        "hub.secret": kwargs.get("secret"),
    }
    response = _formal_get_request(hub_url, "subscription-details", **params)
    parsed = bs4.BeautifulSoup(response.text, "lxml").find_all("dd")
    results = {
        "requests_url": response.url,
        "response_object": response,
        "state": parsed[1].string,
        "stat": parsed[8].string.strip("\n "),
    }
    FIELDS = [
        "last_challenge",
        "expiration",
        "last_subscribe",
        "last_unsubscribe",
        "last_challenge_error",
        "last_notification_error",
        "last_notification",
    ]
    for key, index in zip(FIELDS, list(range(2, 10)) + [10]):
        fuzzy = bool(index == 6 or index == 7)
        results[key] = _parse_detail(parsed[index].string, fuzzy=fuzzy)
    return results
