import logging
from functools import partial
from datetime import datetime
import time
from threading import Thread, Lock
from wled2graph import wled
import webbrowser
import threading
import socket

_LOGGER = logging.getLogger(__name__)

from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.layouts import column
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.palettes import Category10
from bokeh.models import WheelZoomTool, PanTool, Div

# WARNING template is over ridden by bokeh in many cases!
from wled2graph.template import css_template, css_table

data_source = {}
data_lock = Lock()
palette = Category10[10]


# TODO: Need a distinction between those we graph and those we only hover
fields = ['fps', 'rssi', 'bssid']
paths = [['leds', 'fps'], ['wifi', 'rssi'], ['wifi', 'bssid']]


def get_names(args):
    with data_lock:
        for ip in args.ip_list:
            _LOGGER.info(f"getting name for {ip}")
            name, count = wled.get_name(args, ip)
            _LOGGER.info(f"name : LED count = {name} : {count}")
            data_source[str(ip)] = {'name':name, 'count':count, 'x': [], "p": []}
            for field in fields:
                data_source[str(ip)][field] = []


def data_capture(args, start_time):

    while True:
        time.sleep(args.args.period)
        elapsed_time = (datetime.now() - start_time).total_seconds()

        with data_lock:
            for ip in args.ip_list:
                if data_source[str(ip)]['name'] is not None:
                    values = wled.get_param(args, ip, paths)
                    data_source[str(ip)]['x'].append(elapsed_time)
                    for idx, value in enumerate(values):
                        if value is None:
                            continue
                        data_source[str(ip)][fields[idx]].append(value)
                    # get ping for ip
                    new_ping = wled.get_ping(args, ip)
                    data_source[str(ip)]['p'].append(new_ping)


def open_browser():
    webbrowser.open_new("http://localhost:5006")

def make_document(doc, args):
    div_head = Div(
        text=f'<h1 style="font-size: 20px;"><a href="https://github.com/bigredfrog/wled2graph" target="_blank" style="color: inherit;">wled2graph</h1>')
    div_lines = Div(text="<p>Please hold</p>")
    source_dict = {}
    # TODO: create graphs data driven from fields
    size_mode = "stretch_width"
    graph_height = 350

    plot_params = figure(title=f"Real-time update for fps",
                  x_axis_label="time (s)", y_axis_label=f"FPS", width=1500,
                  height=graph_height, sizing_mode=size_mode)

    plot_ping = figure(title="Real-time update for ping",
                  x_axis_label="time (s)", y_axis_label="ping (ms)", width=1500,
                  height=graph_height, x_range=plot_params.x_range,
                  sizing_mode=size_mode)

    plot_rssi = figure(title="Real-time update for rssi",
                  x_axis_label="time (s)", y_axis_label="rssi", width=1500,
                  height=graph_height, x_range=plot_params.x_range,
                  sizing_mode=size_mode)

    for index, ip in enumerate(data_source.keys()):
        # TODO: make this data driven for DICT
        source_dict[ip] = ColumnDataSource(data=dict(x=[], rssi=[], fps=[], bssid=[], p=[]))
        full_name = f"{ip}: {data_source[ip]['name']}"
        plot_params.line("x", "fps",
                  source=source_dict[ip],
                  name=full_name,
                  color=palette[index % len(palette)],
                  legend_label=full_name,
                  line_width=4)

        plot_ping.line("x", "p",
                    source=source_dict[ip],
                    name=full_name,
                    color=palette[index % len(palette)],
                    legend_label=full_name,
                    line_width=4)

        plot_rssi.line("x", "rssi",
                    source=source_dict[ip],
                    name=full_name,
                    color=palette[index % len(palette)],
                    legend_label=full_name,
                    line_width=4)

    plot_params.legend.location = "top_left"
    plot_params.legend.click_policy = "hide"

    plot_ping.legend.location = "top_left"
    plot_ping.legend.click_policy = "hide"

    plot_rssi.legend.location = "top_left"
    plot_rssi.legend.click_policy = "hide"

    xwheel_zoom = WheelZoomTool(dimensions="width")
    plot_params.add_tools(xwheel_zoom)
    plot_params.toolbar.active_scroll = xwheel_zoom
    plot_ping.add_tools(xwheel_zoom)
    plot_ping.toolbar.active_scroll = xwheel_zoom
    plot_rssi.add_tools(xwheel_zoom)
    plot_rssi.toolbar.active_scroll = xwheel_zoom

    x_pan = PanTool(dimensions="width")
    plot_params.add_tools(x_pan)
    plot_params.toolbar.active_drag = x_pan
    plot_ping.add_tools(x_pan)
    plot_ping.toolbar.active_drag = x_pan
    plot_rssi.add_tools(x_pan)
    plot_rssi.toolbar.active_drag = x_pan

    doc.theme = "dark_minimal"

    custom_tooltip = """
        <div style="background: black; margin:-10px; padding: 10px; border-radius: 10px; border: 1px solid white; font-weight: 600; font-size: 14px;">
            <div style="color: white;">key  : $name</div>
            <div style="color: white;">fps  : @fps</div>
            <div style="color: white;">rssi : @rssi</div>
            <div style="color: white;">ping : @p</div>
            <div style="color: white;">bssid: @bssid</div>
        </div>
    """

    hover = HoverTool(tooltips=custom_tooltip)
    plot_params.add_tools(hover)
    plot_ping.add_tools(hover)
    plot_rssi.add_tools(hover)

    def update():
        with data_lock:
            new_table_html = f"<table class='my-table'>"
            new_table_html += f"<tr><th>IP</th><th>Name</th><th>  Leds  </th><th>   FPS   </th><th>BSSID</th><th>  RSSI  </th><th>Ping(ms)</th></tr>"

            for idx, ip in enumerate(data_source.keys()):
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
                        'fps': data_source[ip]['fps'][start_index:],
                        'rssi': data_source[ip]['rssi'][start_index:],
                        'bssid': data_source[ip]['bssid'][start_index:],
                        'p': data_source[ip]['p'][start_index:]
                    }
                    source_dict[ip].stream(new_data, rollover=args.args.rollover)
                cl = Category10[10][idx % 10]
                td_style = f"<td style='color: {cl};'>"
                if data_source[ip]['name'] is None:
                    new_table_html += f"<tr>{td_style}{ip}</td><td>Not Found</td><td></td><td></td><td></td><td></td><td></td></tr>"
                else:
                    new_table_html += f"<tr>{td_style}<a href='http://{ip}' target='_blank' style='color: inherit;'>{ip}</td>"+\
                                      f"{td_style}{data_source[ip]['name']}</td>"+\
                                      f"<td>{data_source[ip]['count']}</td>"+\
                                      f"<td>{data_source[ip]['fps'][-1]}</td>"+\
                                      f"<td>{data_source[ip]['bssid'][-1]}</td>"+\
                                      f"<td>{data_source[ip]['rssi'][-1]}</td>"+\
                                      f"<td>{data_source[ip]['p'][-1]:.0f}</td></tr>"

            new_table_html += '</table>'
            div_lines.text = f"{css_table}{new_table_html}"

    doc.add_periodic_callback(update, args.args.period * 1000)
    doc.template = css_template
    doc.title = "wled2graph"
    doc.add_root(column(div_head, div_lines, plot_params, plot_ping, plot_rssi,
                        sizing_mode="stretch_width"))


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

    if args.args.remote:
        server_settings = {'port': 5006, 'address': '0.0.0.0', 'allow_websocket_origin': ["*"]}
    else:
        server_settings = {'port': 5006, 'address': 'localhost'}

    # Start the Bokeh server with the application
    server = Server({'/': bokeh_app}, **server_settings)
    server.start()

    threading.Thread(target=open_browser).start()

    host_ip = socket.gethostbyname(socket.gethostname())

    _LOGGER.info(
        f"Serving Bokeh app on http://{host_ip}:{server_settings['port']}/")

    # Open a browser or block the program here as needed
    # server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()