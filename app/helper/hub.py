"""
Hub Communicate Related Functions


Build upon PubSubHubbub 0.4 Specification
https://pubsubhubbub.github.io/PubSubHubbub/pubsubhubbub-core-0.4.html

Using Google Hub at
https://pubsubhubbub.appspot.com

"""
import re
import urllib
import bs4
import requests
from dateutil import parser
HUB_GOOGLE_HUB = "https://pubsubhubbub.appspot.com"
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

def _formal_post_request(endpoint, **data):
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
    callback_scheme = urllib.parse.urlparse(data["hub.callback"]).scheme
    if callback_scheme == "http" and data["hub.secret"]:
        raise NonSecureHubSecretError()

    # Sending Requests
    try:
        response = requests.post(
            url=urllib.parse.urljoin(HUB_GOOGLE_HUB, endpoint),
            headers=DEFAULT_HEADERS,
            data=data
        )
        return response
    except requests.exceptions.RequestException:
        return -1

def _formal_get_request(endpoint, **params):
    """
    Required Parameters:
    hub.callback            Subscribers Endpoint
    hub.topic               Content of Subcription

    Optional Parameters:
    hub.secret              Subscriber-provided secret string
    """
    try:
        response = requests.get(
            url=urllib.parse.urljoin(HUB_GOOGLE_HUB, endpoint),
            headers=DEFAULT_HEADERS,
            params=params
        )
        return response
    except requests.exceptions.RequestException:
        return -1

def _parse_detail(query, fuzzy=False):
    try:
        response = parser.parse(query, fuzzy=fuzzy)
        summary = re.search(r"\((.*)\)", query)
        if summary:
            summary = summary.groups()[0]
    except ValueError:
        response = None
        summary = None
    if fuzzy:
        return (response, summary)
    return response

def subscribe(callback_url, topic_url, **kwargs):
    """
    Optional Parameters:
    lease_seconds       Duration of the subscription in seconds
    secret              Subscriber-provided secret string
    """
    data = {
        "hub.callback": callback_url,
        "hub.mode": "subscribe",
        "hub.topic": topic_url,
        "hub.lease_seconds": kwargs.pop("lease_seconds", None),
        "hub.secret": kwargs.pop("secret", None)
    }
    response = _formal_post_request("subscribe", **data)
    if response.status_code == 202:
        response.success = True
    return response

def unsubscribe(callback_url, topic_url, **kwargs):
    """
    Optional Parameters:
    lease_seconds       Duration of the subscription in seconds
    secret              Subscriber-provided secret string
    """
    data = {
        "hub.callback": callback_url,
        "hub.mode": "unsubscribe",
        "hub.topic": topic_url,
        "hub.lease_seconds": kwargs.pop("lease_seconds", None),
        "hub.secret": kwargs.pop("secret", None)
    }
    response = _formal_post_request("subscribe", **data)
    if response.status_code == 202:
        response.success = True
    return response

def details(callback_url, topic_url, **kwargs):
    """
    Optional Parameters:
    secret              Subscriber-provided secret string
    """
    params = {
        "hub.callback": callback_url,
        "hub.topic": topic_url,
        "hub.secret": kwargs.pop("secret", None)
    }
    response_object = _formal_get_request("subscription-details", **params)
    response_soup = bs4.BeautifulSoup(response_object.text, "lxml")
    target = response_soup.find_all("dd")
    response_dict = {
        "requests_url": response_object.url,
        "response_object": response_object,
        "state": target[1].string,
        "stat": target[8].string
    }
    response_dict["last_challenge"] = _parse_detail(target[2].string)
    response_dict["expiration"] = _parse_detail(target[3].string)
    response_dict["last_subscribe"] = _parse_detail(target[4].string)
    response_dict["last_unsubscribe"] = _parse_detail(target[5].string)
    response_dict["last_challenge_error"] = _parse_detail(target[6].string, fuzzy=True)
    response_dict["last_notification_error"] = _parse_detail(target[7].string, fuzzy=True)
    response_dict["last_notification"] = _parse_detail(target[10].string)
    return response_dict
