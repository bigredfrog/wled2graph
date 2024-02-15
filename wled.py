import requests
import logging
import random

_LOGGER = logging.getLogger(__name__)

offline = True


def get_param(args, ip, param):
    if args.args.offline:
        # generate a random number between 10 and 64
        result = random.randint(10, 64)
    else:
        url = f"http://{ip}/json/info"
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()["leds"][param]
#    _LOGGER.info(f"response is {json.dumps(response.json(), indent=4)}")
    return result


def get_name(args, ip):

    if args.args.offline:
        name = f"WLED : {random.randint(1, 256)}"
    else:
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