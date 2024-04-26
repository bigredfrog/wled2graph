# wled2graph
# This program will take a command line of WLED endpoint IP addresses
# It will then set up a bokeh graph server
# It will then set up a polling loop of 5 seconds
# Within that loop it will poll each WLED endpoint for its current json state
# specifically for recovering FPS values
# these will be updated into the graph server

import logging
from wled2graph import utils
from wled2graph import graphs
from wled2graph.args import Args

args = Args()

_LOGGER = logging.getLogger(__name__)

def main():
    utils.setup_logging(logging.INFO)

    args.parse_args()
    _LOGGER.info(f"args are {args.args}")

    graphs.run_bokeh_app(args)

if __name__ == '__main__':
    main()



