import logging
import random

import icmplib
import requests

_LOGGER = logging.getLogger(__name__)

offline = True

# 192.168.1.227, 192.168.1.228,


def get_param(args, ip, paths):
    result = []
    if args.args.offline:
        # generate a random number between 10 and 64
        if random.random() < 0.1:
            result = None
        else:
            for path in paths:
                result.append(random.randint(10, 64))
    elif args.args.no_wled:
        result = None
    else:
        url = f"http://{ip}/json/info"
        try:
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
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"error getting param for {ip} : {e}")
            result = None

    #    _LOGGER.info(f"response is {json.dumps(response.json(), indent=4)}")
    return result


def get_ping(args, ip):
    ###
    # ping the ip address and return the average round trip time
    # if the ping fails, return np.nan which will cause a line
    # break in the graph om bokeh
    ###

    if args.args.offline:
        result = random.randint(10, 100)
    else:
        ping = icmplib.ping(
            address=str(ip),
            count=1,
            privileged=False,
            interval=0.1,
            timeout=1.0,
        )

        # _LOGGER.error(f"{ping}\n{ping.is_alive}")
        if ping.packets_received == 0:
            result = float("nan")
        else:
            result = ping.avg_rtt

    return result


def get_name(args, ip):
    if args.args.offline:
        name = f"WLED{random.randint(1, 100)}"
        count = random.randint(101, 256)
        ver = "0.0.0"
        vid = 1000000
        arch = "unknown"
    elif args.args.no_wled:
        if not hasattr(get_name, "counter"):
            get_name.counter = 1  # Initialize the counter attribute
        name = f"source {get_name.counter}"
        count = 0
        ver = "0.0.0"
        vid = 0
        arch = "NA"
    else:
        url = f"http://{ip}/json/info"
        try:
            response = requests.get(url)
            response.raise_for_status()
            resp_json = response.json()
            #    _LOGGER.info(f"response is {json.dumps(resp_json, indent=4)}")
            name = f"{resp_json['name']}"
            count = f"{resp_json['leds']['count']}"
            ver = resp_json["ver"]
            vid = resp_json["vid"]
            arch = resp_json["arch"]
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"error getting name for {ip} : {e}")
            name = None
            count = None
            ver = None
            vid = None
            arch = None
    return name, count, ver, vid, arch
