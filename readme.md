# WLED2Graph

WLED2Graph is a Python program designed to visualize Frames Per Second (FPS) data from WLED endpoints on a network in real-time using a Bokeh graph server. It sets up a polling loop, defaulting to every 5 seconds, to fetch the current JSON state from each specified WLED endpoint, focusing on recovering and displaying FPS values.

## Features

- **Real-time FPS Visualization**: Continuously polls WLED endpoints and updates the graph with current FPS values.
- **Configurable Polling Frequency**: Allows customization of the polling interval to suit network and performance needs.
- **Scalable**: Can monitor multiple WLED endpoints simultaneously.
- **Customizable Data Points Rollover**: Supports setting a maximum number of data points to display on the graph, after which old data points are rolled off.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.9 or higher

You can install the necessary Python libraries by running:

```bash
pip install -r requirements.txt
```

## Installation
Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/wled2graph.git
cd wled2graph
```

## Usage
WLED2Graph is executed from the command line and requires a list of IP addresses corresponding to the WLED endpoints you wish to monitor.

```bash

python wled2graph.py -w <WLED_IPs> [-p <params>] [-t <time_period>] [-r <rollover>]
```

-w, --wleds: A comma-separated list of IP addresses for the WLED endpoints.  
-t, --time-period: (Optional) The time period in seconds for polling the WLEDs. Default is 5 seconds.  
-r, --rollover: (Optional) The number of data points to keep in the graph before rolling over. Default is 20000.  

This is not currently supported

-p, --params: (Optional) A comma-separated list of parameters to log. Currently, only fps is supported.

### Example
To start monitoring two WLED endpoints with a polling interval of 10 seconds:

```bash
python wled2graph.py -w 192.168.1.100,192.168.1.101 -t 10
```

To start monitoring five WLED endpoints with a polling interval of 1 seconds and a data point rollover of 30:

```bash
python wled2graph.py -w "192.168.1.216, 192.168.1.217, 192.168.1.220, 192.168.1.229, 192.168.1.230" -t 1 -r 30
```
Contributing
I just don't know if this has legs right now...

License
This project is licensed under the MIT License - see the LICENSE.md file for details.

https://github.com/bigredfrog/wled2graph/blob/master/license.md
