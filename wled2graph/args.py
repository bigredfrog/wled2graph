import logging
import argparse
import ipaddress

_LOGGER = logging.getLogger(__name__)

def process_ip_list(ip_list_str):
    # Split the string into individual IP addresses
    ip_list = ip_list_str.split(',')

    # Check if there is at least one IP address
    if not ip_list:
        raise argparse.ArgumentTypeError("At least one IP address is required")

    # Validate each IP address in the list and convert them to ipaddress objects
    ip_objects = []
    for ip_str in ip_list:
        try:
            ip_objects.append(ipaddress.IPv4Address(
                ip_str.strip()))  # Create ipaddress object
        except ipaddress.AddressValueError:
            raise argparse.ArgumentTypeError(f"Invalid IP address: {ip_str}")

    # sort list by ip address
    ip_objects.sort()
    return ip_objects


def process_fields(input_string):
    # Split the string by commas
    tokens = input_string.split(',')
    # Replace spaces with underscores in each token
    processed_tokens = [token.strip().replace(' ', '_') for token in tokens]
    return processed_tokens


# define an args class
class Args:
    args = None
    ip_list = None
    params = None

    def __init__(self):
        self.parse_args()

        self.ip_list = process_ip_list(self.args.wleds)
        _LOGGER.info(f"ips are {self.ip_list}")

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description="A Networked LED Effect Controller"
        )

        parser.add_argument(
            "-w",
            "--wleds",
            dest="wleds",
            help="comma seperated list of ip addresses",
            required=True,
            type=str,
        )

        parser.add_argument(
            "-t",
            "--time-period",
            dest="period",
            help="float value of time period to poll the WLEDs, default is 5",
            default=5.0,
            type=float,
        )

        parser.add_argument(
            "-r",
            "--rollover",
            dest="rollover",
            help="int value to rollover the points default is 20000",
            default=20000,
            type=int,
        )

        parser.add_argument(
            "-o",
            "--offline",
            dest="offline",
            help="simulate the WLED endpoints, default is False",
            action="store_true",
        )

        parser.add_argument(
            "-m",
            "--remote",
            dest="remote",
            help="allow remote access to server, default is False",
            action="store_true",
        )

        self.args = parser.parse_args()
