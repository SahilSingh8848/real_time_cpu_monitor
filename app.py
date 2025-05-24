import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import psutil
import plotly.graph_objs as go
import dash_daq as daq
import time
import threading
import platform
import os

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("System Performance Monitor", style={'textAlign': 'center', 'color': '#222831', 'marginBottom': '20px'}),

    html.Div([
        daq.Gauge(id='cpu-gauge', label='CPU Usage (%)', min=0, max=100, value=0, showCurrentValue=True, color="#f44336"),
        daq.Gauge(id='ram-gauge', label='RAM Usage (%)', min=0, max=100, value=0, showCurrentValue=True, color="#2196f3"),
        daq.Gauge(id='disk-gauge', label='Disk Usage (%)', min=0, max=100, value=0, showCurrentValue=True, color="#4caf50"),
        daq.Gauge(id='network-gauge', label='Network KB/s', min=0, max=10000, value=0, showCurrentValue=True, color="#ff9800"),
    ], style={'display': 'flex', 'justifyContent': 'space-around'}),

    dcc.Interval(id='interval-component', interval=1000, n_intervals=0),

    html.Div([
        dcc.Graph(id='cpu-graph'),
        dcc.Graph(id='ram-graph'),
        dcc.Graph(id='disk-graph'),
        dcc.Graph(id='memory-graph'),
        dcc.Graph(id='network-graph'),
    ]),

    html.H2("Processes", style={'textAlign': 'center', 'marginTop': '20px'}),
    dash_table.DataTable(
        id='top-processes',
        columns=[
            {'name': 'PID', 'id': 'pid'},
            {'name': 'Name', 'id': 'name'},
            {'name': 'CPU %', 'id': 'cpu'},
            {'name': 'Memory %', 'id': 'memory'},
            {'name': 'Disk MB', 'id': 'disk'},
            {'name': 'Status', 'id': 'status'},
            {'name': 'User', 'id': 'username'},
            {'name': 'Description', 'id': 'description'},
            {'name': 'Architecture', 'id': 'architecture'},  # NEW COLUMN
        ],
        style_table={'overflowX': 'auto', 'padding': '10px'},
        style_cell={'backgroundColor': '#ffffff', 'color': '#000000', 'textAlign': 'center'},
        style_header={'backgroundColor': '#eeeeee', 'fontWeight': 'bold'}
    ),
], style={'backgroundColor': '#f5f5f5', 'padding': '10px'})

# Store history
time_series = {'cpu': [], 'ram': [], 'disk': [], 'memory': [], 'network': [], 'time': []}

# Background thread to update system metrics
def update_metrics():
    prev_bytes_sent = prev_bytes_recv = 0
    while True:
        cpu_usage = psutil.cpu_percent(interval=None)
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        memory_usage = psutil.swap_memory().percent

        net_io = psutil.net_io_counters()
        bytes_sent = net_io.bytes_sent
        bytes_recv = net_io.bytes_recv

        if prev_bytes_sent == 0 and prev_bytes_recv == 0:
            prev_bytes_sent, prev_bytes_recv = bytes_sent, bytes_recv
            network_usage = 0
        else:
            network_usage = ((bytes_sent - prev_bytes_sent) + (bytes_recv - prev_bytes_recv)) / 1024  # KB/s

        prev_bytes_sent, prev_bytes_recv = bytes_sent, bytes_recv

        current_time = time.strftime('%H:%M:%S')

        time_series['cpu'].append(cpu_usage)
        time_series['ram'].append(ram_usage)
        time_series['disk'].append(disk_usage)
        time_series['memory'].append(memory_usage)
        time_series['network'].append(network_usage)
        time_series['time'].append(current_time)

        if len(time_series['cpu']) > 50:
            for key in time_series:
                time_series[key].pop(0)

        time.sleep(1)

# Start background thread
threading.Thread(target=update_metrics, daemon=True).start()

# Get Top Processes with additional fields
def get_top_processes():
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'io_counters', 'status', 'username', 'exe']):
        try:
            io = proc.info['io_counters']
            disk_mb = (io.read_bytes + io.write_bytes) / (1024 * 1024) if io else 0
            exe_path = proc.info['exe']
            arch = 'Unknown'
            if exe_path and os.path.exists(exe_path):
                arch_tuple = platform.architecture(exe_path)[0]
                arch = 'x64' if '64' in arch_tuple else 'x86'

            procs.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu': round(proc.info['cpu_percent'], 2),
                'memory': round(proc.info['memory_percent'], 2),
                'disk': round(disk_mb, 2),
                'status': proc.info['status'],
                'username': proc.info['username'],
                'description': exe_path if exe_path else 'N/A',
                'architecture': arch,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
            pass
    procs = sorted(procs, key=lambda x: x['cpu'], reverse=True)
    return procs[:20]

# Callback to update dashboard
@app.callback(
    [
        Output('cpu-gauge', 'value'),
        Output('ram-gauge', 'value'),
        Output('disk-gauge', 'value'),
        Output('network-gauge', 'value'),
        Output('cpu-graph', 'figure'),
        Output('ram-graph', 'figure'),
        Output('disk-graph', 'figure'),
        Output('memory-graph', 'figure'),
        Output('network-graph', 'figure'),
        Output('top-processes', 'data')
    ],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    cpu_usage = time_series['cpu'][-1] if time_series['cpu'] else 0
    ram_usage = time_series['ram'][-1] if time_series['ram'] else 0
    disk_usage = time_series['disk'][-1] if time_series['disk'] else 0
    network_usage = time_series['network'][-1] if time_series['network'] else 0

    def create_graph(y_data, title, y_title):
        fig = go.Figure(data=[go.Scatter(x=time_series['time'], y=y_data, mode='lines+markers')])
        fig.update_layout(title=title, xaxis_title='Time', yaxis_title=y_title, template='plotly_white')
        return fig

    top_procs = get_top_processes()

    return (
        cpu_usage, ram_usage, disk_usage, network_usage,
        create_graph(time_series['cpu'], "CPU Usage Over Time", "CPU %"),
        create_graph(time_series['ram'], "RAM Usage Over Time", "RAM %"),
        create_graph(time_series['disk'], "Disk Usage Over Time", "Disk %"),
        create_graph(time_series['memory'], "Memory Usage Over Time", "Memory %"),
        create_graph(time_series['network'], "Network Usage Over Time", "KB/s"),
        top_procs
    )

if __name__ == '__main__':
    app.run_server(debug=True)
