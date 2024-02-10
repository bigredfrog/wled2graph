import logging
from logging.handlers import RotatingFileHandler
import ipaddress


def setup_logging(loglevel):
    console_loglevel = loglevel or logging.WARNING
    console_logformat = "[%(levelname)-8s] %(name)-30s : %(message)s"

    file_loglevel = loglevel or logging.INFO
    file_logformat = "%(asctime)-8s %(name)-30s %(levelname)-8s %(message)s"

    root_logger = logging.getLogger()

    file_handler = RotatingFileHandler(
        "wled2graph.log",
        mode="a",  # append
        maxBytes=0.5 * 1000 * 1000,  # 512kB
        encoding="utf8",
        backupCount=5,  # once it hits 2.5MB total, start removing logs.
    )
    file_handler.setLevel(file_loglevel)  # set loglevel
    file_formatter = logging.Formatter(file_logformat)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_loglevel)  # set loglevel
    console_formatter = logging.Formatter(
        console_logformat
    )  # a simple console format
    console_handler.setFormatter(
        console_formatter
    )  # tell the console_handler to use this format

    # add the handlers to the root logger
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Suppress some of the overly verbose logs
    logging.getLogger("sacn").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
    logging.getLogger("zeroconf").setLevel(logging.WARNING)

    global _LOGGER
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

    return ip_objects


def process_fields(input_string):
    # Split the string by commas
    tokens = input_string.split(',')
    # Replace spaces with underscores in each token
    processed_tokens = [token.strip().replace(' ', '_') for token in tokens]
    return processed_tokens


