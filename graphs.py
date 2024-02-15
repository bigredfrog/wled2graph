import logging
from functools import partial
from datetime import datetime
import time
from threading import Thread, Lock
import wled
import webbrowser
import threading

_LOGGER = logging.getLogger(__name__)

from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.layouts import column
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.palettes import Category10
from bokeh.models import WheelZoomTool, PanTool

data_source = {}
data_lock = Lock()
palette = Category10[10]

def get_names(args):
    with data_lock:
        for ip in args.ip_list:
            _LOGGER.info(f"getting name for {ip}")
            name = wled.get_name(args, ip)
            _LOGGER.info(f"name : LED count = {name}")
            data_source[str(ip)] = {"name":name, 'x': [], 'y': []}


def data_capture(args, start_time):

    while True:
        time.sleep(args.args.period)
        elapsed_time = (datetime.now() - start_time).total_seconds()

        with data_lock:
            for ip in args.ip_list:
                # make a call to the WLED JSON api and get the value of the param
                if data_source[str(ip)]['name'] is not None:
                    new_value = wled.get_param(args, ip, args.params[0])
                    data_source[str(ip)]['x'].append(elapsed_time)
                    data_source[str(ip)]['y'].append(new_value)


def open_browser():
    webbrowser.open_new("http://localhost:5006")

def make_document(doc, args):

    source_dict = {}
    param = args.params[0]
    plot = figure(title=f"Real-time update for {param}",
                  x_axis_label="time (s)", y_axis_label=f"{param}", width=1500,
                  height=750)

    for index, ip in enumerate(data_source.keys()):
        source_dict[ip] = ColumnDataSource(data=dict(x=[], y=[]))
        full_name = f"{ip}: {data_source[ip]['name']}"
        plot.line("x", "y",
                  source=source_dict[ip],
                  name=full_name,
                  color=palette[index % len(palette)],
                  legend_label=full_name,
                  line_width=4)

    plot.legend.location = "top_left"
    plot.legend.click_policy = "hide"

    xwheel_zoom = WheelZoomTool(dimensions="width")
    plot.add_tools(xwheel_zoom)
    plot.toolbar.active_scroll = xwheel_zoom
    x_pan = PanTool(dimensions="width")
    plot.add_tools(x_pan)
    plot.toolbar.active_drag = x_pan
    doc.theme = "dark_minimal"

    custom_tooltip = """
        <div style="background: black; margin:-10px; padding: 10px; border-radius: 10px; border: 1px solid white; font-weight: 600; font-size: 14px;">
            <div style="color: white;">key: $name</div>
            <div style="color: white;">fps: @y</div>
        </div>
    """

    hover = HoverTool(tooltips=custom_tooltip)
    plot.add_tools(hover)

    def update():
        with data_lock:
            for ip in data_source.keys():
                x_values = source_dict[ip].data['x']
                last_x = x_values[-1] if x_values else -float('inf')

                # Find the index to start streaming from by walking backwards through the X range
                start_index = None
                for i in range(len(data_source[ip]['x']) - 1, -1, -1):
                    if data_source[ip]['x'][i] <= last_x:
                        break
                    start_index = i

                # If there are new points to add
                if start_index is not None:
                    # It means we have new data points to stream
                    new_data = {
                        'x': data_source[ip]['x'][start_index:],
                        'y': data_source[ip]['y'][start_index:]
                    }
                    source_dict[ip].stream(new_data, rollover=args.args.rollover)

    doc.add_periodic_callback(update, args.args.period * 1000)
    doc.add_root(column(plot))


def run_bokeh_app(args):
    start_time = datetime.now()

    get_names(args)

    # Start data capture in a background thread
    data_thread = Thread(target=data_capture, args=(args, start_time))
    data_thread.daemon = True  # Ensures the thread exits when the main program does
    data_thread.start()

    logging.getLogger('bokeh').setLevel(logging.INFO)

    # Create the Bokeh application
    bokeh_app = Application(FunctionHandler(partial(make_document, args=args)))

    # Define server settings here as needed
    server_settings = {'port': 5006, 'address': 'localhost'}

    # Start the Bokeh server with the application
    server = Server({'/': bokeh_app}, **server_settings)
    server.start()

    threading.Thread(target=open_browser).start()

    _LOGGER.info(
        f"Serving Bokeh app on http://{server_settings['address']}:{server_settings['port']}/")

    # Open a browser or block the program here as needed
    # server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()