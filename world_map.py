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
    def __init__(self, controller,app):
        # Initialization method with a controller parameter for external interactions
        self.controller = controller
        self.app = app

        # Setting up publication and server details
        self.publisher = "visualization/worldmap"
       

        # Reading data from a JSON file
        data_path = os.path.join('..', 'data', 'summary.json')
        self.df = self.read_data(data_path)

        # Hidding the mode bar
        self.config = {'displayModeBar': False}

        # Setting up the Dash web application
        self.world_map()


    def read_data(self, filename):
        # Method to load data from a JSON file into a DataFrame
        df = pd.read_json(filename, orient="records")
        # Transform the 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'],format='%Y%m%d')
        return df

    def create_world_map_fig(self):
        # Method to create a Plotly figure for a world map visualization
        fig = px.scatter_geo(
            self.df,
            lat="lat",
            lon="lon",
            color="Objects/ml",  # Column for marker color
            projection="natural earth",
            color_continuous_scale=px.colors.sequential.Bluered,  # Using a predefined color scale
            hover_data={"filename": True,"date":True,"Objects/ml": ":.2f","lat": ":.0f","lon": ":.0f"} # Displaying additional data on hover
        )

        # Updating figure layout and trace properties
        fig.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, t=0, b=0),
            height=None,
            width=None
        )

        # Updating marker properties
        size = [10] * len(self.df)
        opacity = [0.5] * len(self.df)
        fig.update_traces(marker=dict(size=size, opacity=opacity))

        # Adjusting color axis properties for the color bar
        fig.update_coloraxes(colorbar=dict(
            thickness=10,  # Adjusting color bar thickness
            len=0.9,  # Adjusting color bar length
            yanchor="middle",  # Vertically anchoring at the middle
            y=0.5,  # Vertically positioning at the middle
        ))

        return fig

    def world_map(self):
        # Method to setup and run the Dash web application
        self.fig = self.create_world_map_fig()


        # Defining the layout of the web application
        self.app.layout = html.Div([
            dcc.Graph(id='world-map', figure=self.fig, clear_on_unhover=True,config=self.config,
                      style={'position': 'relative', 'flex':1})
        ],
            style={'position': 'relative', 
                   'display': 'flex',
                   'margin': 0,
                   'padding': 0,
                   'overflow': 'hidden',
                   'align-items': 'center',
                   'justify-content': 'center'
                   }
        )

        @self.app.callback(
            Output('world-map', 'figure'),
            Input('world-map', 'clickData')
        )
        def select_point(clickData):
            # Callback function to handle click events on the world map
            if clickData is None:
                return no_update

            # Highlighting the selected point on the world map
            selected_point = clickData['points'][0]
            selected_point['marker.opacity'] = 1

            # Updating the figure with the highlighted point
            opacity = [1 if i == selected_point['pointNumber'] else 0.5 for i in range(len(self.df))]
            self.fig.update_traces(marker=dict(opacity=opacity))           

            return self.fig

       
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

    app = Dash(__name__)  # Creating an instance of Dash for the web application
    world_map = WorldMap(None,app)  # Creating an instance of WorldMap without a controller for demonstration
    app.run(debug=True, use_reloader=False)  # Running the web application