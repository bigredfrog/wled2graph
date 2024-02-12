import requests
import logging
import json

_LOGGER = logging.getLogger(__name__)

def get_param(ip, param):
    url = f"http://{ip}/json/info"
    response = requests.get(url)
    response.raise_for_status()
#    _LOGGER.info(f"response is {json.dumps(response.json(), indent=4)}")
    return response.json()["leds"][param]

def get_name(ip):
    url = f"http://{ip}/json/info"
    try:
        response = requests.get(url)
        response.raise_for_status()
        resp_json = response.json()
#    _LOGGER.info(f"response is {json.dumps(resp_json, indent=4)}")
        name = f"{resp_json['name']} : {resp_json['leds']['count']}"
    except requests.exceptions.RequestException as e:
        _LOGGER.error(f"error getting name for {ip} : {e}")
        name = None
    return name