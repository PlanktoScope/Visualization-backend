import plotly.express as px
from dash import dcc, html, Input, Output, no_update, callback
from PIL import Image
import io
import base64
import os
import requests
import re
from flask import request
import json
import zipfile

import utils

class ScatterPlot:
    def __init__(self,controller,app, df, x, y):
        self.controller = controller
        self.app=app
        self.df = df
        self.x = x
        self.y = y

        self.publisher = "visualization/chartPage"

        # Remove unwanted buttons from the plotly graph
        self.config = {
            'modeBarButtonsToRemove': ["select", "zoomIn", "zoomOut", "autoScale"],
            'displaylogo': False
        }

        self.scatter_plot()

    def create_scatter_fig(self):
        # Create a scatter plot figure with custom data for images
        fig = px.scatter(
            data_frame=self.df,
            x=self.x,
            y=self.y,
            custom_data=["img_file_name"],
            title=self.df.name
        )
        fig.update_traces(mode='markers', marker_line_width=1, marker_size=8,marker_opacity=0.3, marker_color='#a3a7e4',
                          hoverinfo='none', hovertemplate=None)

        # Add a title to the figure


        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=list([
                        dict(label="Lin",
                             method="relayout",
                             args=[{"yaxis.type": "linear"}]
                             ),
                        dict(label="Log",
                             method="relayout",
                             args=[{"yaxis.type": "log"}]
                             )
                    ]),
                    type="buttons",
                    pad= {'r': 0, 't': 0, 'b': 0, 'l': 0},
                    direction="down",
                    showactive=True,
                    x=-0.30,
                    xanchor="left",
                    y=1.1,
                    yanchor="top"
                ),
                dict(
                    buttons=list([
                        dict(label="Lin",
                             method="relayout",
                             args=[{"xaxis.type": "linear"}]
                             ),
                        dict(label="Log",
                             method="relayout",
                             args=[{"xaxis.type": "log"}]
                             )
                    ]),
                    type="buttons",
                    pad= {'r': 0, 't': 0, 'b': 0, 'l': 0},
                    direction="right",
                    showactive=True,
                    x=0.90,
                    xanchor="left",
                    y=-0.10,
                    yanchor="top"
                ),
            ]
        )
        return fig  # Return the created figure

    def scatter_plot(self):

        fig = self.create_scatter_fig()  # Create scatter plot figure

        self.app.layout = html.Div([
            dcc.Graph(id='scatter-plot', figure=fig, config=self.config,clear_on_unhover=True),
            dcc.Tooltip(id="graph-tooltip-2", direction='bottom'),
            html.Button('X', id='stop-button', n_clicks=0,
                        style={'position': 'absolute', 'top': 10, 'left': 10,
                               'background-color': 'red', 'color': 'white'})
        ],
            style={'position': 'relative', 'width': '100%', 'height': '100%'}
        )

        @self.app.callback(
            Output("graph-tooltip-2", "show"),
            Output("graph-tooltip-2", "bbox"),
            Output("graph-tooltip-2", "children"),
            Output("graph-tooltip-2", "direction"),
            Input("scatter-plot", "hoverData"), 
        )
        def display_hover(hoverData):
            # Display the tooltip with image on hover

            if hoverData is None:
                print("No hover data")
                return False, no_update, no_update, no_update

            pt = hoverData["points"][0]
            img_file_name = pt["customdata"][0]
            print(f"Hover data received: {img_file_name}")

            if(self.df.zip==False):
                # Load image with pillow
                image_path = os.path.dirname(self.df.path) + "/" + img_file_name

                try:
                    im = Image.open(image_path)
                    buffer = io.BytesIO()
                    im.save(buffer, format="jpeg")
                    encoded_image = base64.b64encode(buffer.getvalue()).decode()
                    im_url = "data:image/jpeg;base64," + encoded_image
                except Exception as e:
                    print(f"Error loading image: {e}")
                    return False, no_update, no_update, no_update
            else:
                # Load image from zip
                try:
                    zip_path, inner_path = self.df.path.split('zip:', 1)
                    zip_path=zip_path+'zip'
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        with zip_ref.open(img_file_name) as file:
                            im = Image.open(file)
                            buffer = io.BytesIO()
                            im.save(buffer, format="jpeg")
                            encoded_image = base64.b64encode(buffer.getvalue()).decode()
                            im_url = "data:image/jpeg;base64," + encoded_image
                except Exception as e:
                    print(f"Error loading image from ZIP: {e}")
                    return False, no_update, no_update, no_update

            hover_data = hoverData["points"][0]
            bbox = hover_data["bbox"]

            y = hover_data["y"]
            direction = "bottom" if y > 1.5 else "top"

            children = [
                html.Img(
                    src=im_url,
                    style={"width": "150px"},
                ),
                html.P(img_file_name),
            ]

            return True, bbox, children, direction
        


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
                msg={"command":"remove iframe","src":f"{base_url[:-1]}{self.app.get_relative_path('')}"}
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

    # Scatter plot
    scatter_plot = ScatterPlot(None, df, x, y)

    input("Press Enter to stop the main thread")
