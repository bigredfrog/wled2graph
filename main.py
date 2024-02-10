# wled2graph
# This program will take a command line of WLED endpoint IP addresses
# It will then set up a bokeh graph server
# It will then set up a polling loop of 5 seconds
# Within that loop it will poll each WLED endpoint for its current json state
# specifically for recovering FPS values
# these will be updated into the graph server

import bokeh
import logging
import argparse
import utils
import graphs


_LOGGER = logging.getLogger(__name__)


def parse_args():
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
        "-p",
        "--params",
        dest="params",
        help="comma seperated list of params to attempt to log, default is fps",
        default="fps",
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

    return parser.parse_args()



if __name__ == '__main__':
    utils.setup_logging(logging.DEBUG)
    # use argsys library to get the command line arguments
    # this will be a list of WLED endpoints
    args = parse_args()
    _LOGGER.info(f"args are {args}")

    ip_list = utils.process_ip_list(args.wleds)
    _LOGGER.info(f"ips are {ip_list}")

    params = utils.process_fields(args.params)
    _LOGGER.info(f"params are {params}")

    # Set up the bokeh instances
    # for param in params:
    #     _LOGGER.info(f"param is {param}")
    #     p = figure(title=f"{param} real time", x_axis_label='time', y_axis_label=param)

    graphs.run_bokeh_app(args, ip_list, params)



