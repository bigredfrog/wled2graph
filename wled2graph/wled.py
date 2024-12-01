import numpy as np
import requests
import logging
import random
import icmplib

_LOGGER = logging.getLogger(__name__)

offline = True

# 192.168.1.227, 192.168.1.228,

def get_param(args, ip, paths):
    result = []
    if args.args.offline:
        # generate a random number between 10 and 64
        for path in paths:
            result.append(random.randint(10, 64))
    else:
        url = f"http://{ip}/json/info"
        response = requests.get(url)
        # only uncomment this line for development debug
        # response.raise_for_status()
        json_data = response.json()
        for path in paths:
            # Navigate through the JSON structure using each key in the path
            value = json_data
            for key in path:
                value = value.get(key)
                if value is None:
                    # If any intermediate key is missing, break and append None
                    result.append(None)
                    break
            else:
                result.append(value)
#    _LOGGER.info(f"response is {json.dumps(response.json(), indent=4)}")
    return result


def get_ping(args, ip):
    ###
    # ping the ip address and return the average round trip time
    # if the ping fails, return np.nan which will cause a line
    # break in the graph om bokeh
    ###

    ping = icmplib.ping(
        address=str(ip),
        count=1,
        privileged=False,
        interval=0.1,
        timeout=0.500,
    )

    if ping.packets_received == 0:
        result = np.nan
    else:
        result = ping.avg_rtt
    return result



def get_name(args, ip):

    if args.args.offline:
        name = f"WLED{random.randint(1, 100)}"
        count = random.randint(101, 256)
    else:
        url = f"http://{ip}/json/info"
        try:
            response = requests.get(url)
            response.raise_for_status()
            resp_json = response.json()
    #    _LOGGER.info(f"response is {json.dumps(resp_json, indent=4)}")
            name = f"{resp_json['name']}"
            count = f"{resp_json['leds']['count']}"
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"error getting name for {ip} : {e}")
            name = None
            count = None
    return name, count