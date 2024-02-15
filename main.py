# wled2graph
# This program will take a command line of WLED endpoint IP addresses
# It will then set up a bokeh graph server
# It will then set up a polling loop of 5 seconds
# Within that loop it will poll each WLED endpoint for its current json state
# specifically for recovering FPS values
# these will be updated into the graph server

import bokeh
import logging
import utils
import graphs
from args import Args

args = Args()

_LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    utils.setup_logging(logging.INFO)

    args.parse_args()
    _LOGGER.info(f"args are {args}")

    graphs.run_bokeh_app(args)



