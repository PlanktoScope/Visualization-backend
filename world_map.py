# Importing necessary libraries for data visualization, web application development, data manipulation, and threading
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, no_update, callback
import json
import pandas as pd
import os
import threading

# Importing a custom utility module
import utils

# Definition of the WorldMap class
class WorldMap:
    def __init__(self, controller):
        # Initialization method with a controller parameter for external interactions
        self.controller = controller

        # Initializing class attributes for state management and configuration
        self.done = False
        self.ready_event = threading.Event()  # Event to signal readiness

        # Setting up publication and server details
        self.publisher = "visualization/worldmap"
        self.port = utils.find_first_available_local_port()
        self.ip_address = utils.get_raspberry_pi_ip()
        self.url = f"http://{self.ip_address}:{self.port}/"

        # Reading data from a JSON file
        data_path = os.path.join('..', 'data', 'datasets.json')
        self.df = self.read_data("data/datasets.json")

        # Initializing and starting a thread for the web application
        self.thread = None
        self.start_thread()

    def read_data(self, filename):
        # Method to load data from a JSON file into a DataFrame
        df = pd.read_json(filename, orient="records")
        return df

    def create_world_map_fig(self):
        # Method to create a Plotly figure for a world map visualization
        fig = px.scatter_geo(
            self.df,
            lat="lat",
            lon="lon",
            color="number_of_objects",  # Column for marker color
            projection="natural earth",
            color_continuous_scale=px.colors.sequential.Bluered,  # Using a predefined color scale
        )

        # Updating figure layout and trace properties
        fig.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, t=0, b=0),
            height=None,
            width=None
        )

        fig.update_traces(
            marker=dict(size=10, opacity=0.6)
        )

        # Adjusting color axis properties for the color bar
        fig.update_coloraxes(colorbar=dict(
            thickness=10,  # Adjusting color bar thickness
            len=0.7,  # Adjusting color bar length
            yanchor="middle",  # Vertically anchoring at the middle
            y=0.5,  # Vertically positioning at the middle
        ))

        return fig

    def world_map(self):
        # Method to setup and run the Dash web application
        fig = self.create_world_map_fig()

        app = Dash(__name__)

        # Defining the layout of the web application
        app.layout = html.Div([
            dcc.Graph(id='world-map', figure=fig, clear_on_unhover=True,
                      style={'position': 'relative', 'width': '100%', 'height': '100%'}),
            html.Div(id='app-status'),
            dcc.Store(id='app-state', data={'ready': False})  # Storing application state
        ],
            style={'position': 'relative', 'width': '100%', 'height': '100%'}
        )

        # Callbacks to update application state and display status
        @app.callback(
            Output('app-state', 'data'),
            Input('world-map', 'figure')
        )
        def update_app_state(fig):
            if fig:
                self.ready_event.set()  # Trigger event when figure is ready
                return {'ready': True}
            return {'ready': False}

        @app.callback(
            Output('app-status', 'children'),
            Input('app-state', 'data')
        )
        def display_app_status(state):
            return '' if state['ready'] else 'Application is loading'

        # Running the Dash application
        app.run(debug=False, host=self.ip_address, port=self.port, use_reloader=False)
        print(f"Server running at {self.url}")

    def start_thread(self):
        # Method to start a thread for running the Dash application
        self.thread = utils.ControlledThread(target=self.world_map)
        self.thread.start()

        # Starting a separate thread to monitor application state
        monitoring_thread = threading.Thread(target=self.monitor_app_state)
        monitoring_thread.start()

    def monitor_app_state(self):
        # Method to monitor when the application is ready
        self.ready_event.wait()  # Waiting for the event to be triggered
        self.done = True
        print('WorldMap is ready')

    def stop_thread(self):
        # Method to stop the Dash application thread
        msg = {"command": "remove iframe", "src": self.url}
        self.controller.publish(self.publisher, json.dumps(msg))
        self.thread.kill()
        self.thread.join()
        print("Server stopped at", self.url)

# Example usage section
if __name__ == "__main__":
    # Manually creating a DataFrame with adjusted latitude and longitude coordinates to simulate data
    data = [
        {"filename": "dataset1.tsv", "number_of_objects": 100, "lat": 0, "lon": -30},
        {"filename": "dataset2.tsv", "number_of_objects": 200, "lat": 10, "lon": -40},
        {"filename": "dataset3.tsv", "number_of_objects": 300, "lat": -20, "lon": -30},
        {"filename": "dataset4.tsv", "number_of_objects": 400, "lat": -10, "lon": 150},
        {"filename": "dataset5.tsv", "number_of_objects": 500, "lat": 0, "lon": 160}
    ]

    df = pd.DataFrame(data)
    world_map = WorldMap(None)  # Creating an instance of WorldMap without a controller for demonstration