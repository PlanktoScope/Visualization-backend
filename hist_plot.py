import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import json
import requests
import re
from flask import request

import utils as utils


class HistPlot:
    def __init__(self,controller,app, df, x):
        self.controller = controller
        self.app=app
        self.df = df
        self.x = x
        

        self.publisher = "visualization/chartPage"

        # Remove unwanted buttons from the plotly graph
        self.config = {
            'modeBarButtonsToRemove': ["select", "zoomIn", "zoomOut", "autoScale"],
            'displaylogo': False
        }
        
        self.hist_plot()

    def create_hist_fig(self):
        # Create a Plotly Express histogram
        fig = px.histogram(data_frame=self.df, x=self.x,title=self.df.name)
        fig.update_traces(marker_color='#a3a7e4')

        # Create buttons for standard units and percentages
        normalization_buttons = [
            {
                'label': 'Count',
                'method': 'update',
                'args': [
                    {'histnorm': ''},  # Update the normalization
                    {'yaxis': {'title': 'Count'}}  # Update the y-axis title
                ]
            },
            {
                'label': 'Percentage',
                'method': 'update',
                'args': [
                    {'histnorm': 'percent'},  # Update the normalization
                    {'yaxis': {'title': 'Percentage'}}  # Update the y-axis title
                ]
            }
        ]

        # Create buttons for linear and log scale
        scale_buttons = [
            {
                'label': 'Linear Scale',
                'method': 'update',
                'args': [
                    {'xaxis': {'type': 'linear'}},  # Update the x-axis to linear scale
                ]
            },
            {
                'label': 'Log Scale',
                'method': 'update',
                'args': [
                    {'xaxis': {'type': 'log'}},  # Update the x-axis to log scale
                ]
            }
        ]

        # Add buttons to the figure
        fig.update_layout(
            updatemenus=[
                {
                    'buttons': normalization_buttons,
                    'direction': 'left',
                    'pad': {'r': 0, 't': 0, 'b': 0, 'l': 0},
                    'showactive': True,
                    'type': 'buttons',
                    'x': 0.1,
                    'xanchor': 'left',
                    'y': 1.15,
                    'yanchor': 'top'
                }
                # ,
                # {
                #     'buttons': scale_buttons,
                #     'direction': 'left',
                #     'pad': {'r': 10, 't': 10},
                #     'showactive': True,
                #     'type': 'buttons',
                #     'x': 0.5,
                #     'xanchor': 'left',
                #     'y': 1.1,
                #     'yanchor': 'top'
                # }
            ]
        )
        return fig

    def hist_plot(self):
        fig = self.create_hist_fig()
        


        self.app.layout = html.Div([
            dcc.Graph(id='hist-plot', figure=fig, config=self.config),
            html.Div(id='output-div'),
            html.Button('X', id='stop-button', n_clicks=0,
                        style={'position': 'absolute', 'top': 10, 'left': 10,
                               'background-color': 'red', 'color': 'white'})
        ],
            style={'position': 'relative', 'width': '100%', 'height': '100%'}
        )

        
        @self.app.callback(
        Input('stop-button', 'n_clicks')
        )
        def shutdown(n_clicks):

            # Use regular expression to find app_id
            match = re.search(r'.*(\d+)/', self.app.config['requests_pathname_prefix'])
            if match:
                app_id = match.group(1)
                print(f"Shutting down app {app_id}")
                # Get the base URL of the server
                base_url = request.host_url
                # Post request to shutdown the app with app_id
                shutdown_url = f"{base_url}apps/shutdown"
                msg={"command":"remove iframe","src":f"{self.app.get_relative_path('')}"}
                self.controller.publish(self.publisher, json.dumps(msg))
                response = requests.post(shutdown_url, data={'app_id': app_id})
                print(f"Shutdown response: {response.text}")
            else:
                print("App ID not found")

        
        

# Example usage
if __name__ == "__main__":
    # Example DataFrame df and columns x, y
    df = px.data.iris()
    x = 'sepal_width'
    y = 'sepal_length'
    df['img_file_name'] = [f"img_{i}.png" for i in range(len(df))]


    #hist plot
    hist_plot = HistPlot(df, x, y)

    input("Press Enter to stop the main thread")


