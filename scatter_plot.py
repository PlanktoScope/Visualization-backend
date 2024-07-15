import plotly.express as px
from dash import Dash, dcc, html, Input, Output, no_update, callback
from PIL import Image
import io
import base64
import json
import os

import utils
import utils

class ScatterPlot:
    def __init__(self, controller, df, x, y):
        self.controller = controller
        self.df = df
        self.x = x
        self.y = y

        self.done = False

        self.publisher = "visualization/chartPage"
        self.port = utils.find_first_available_local_port()
        self.ip_address = utils.get_raspberry_pi_ip()
        self.url = f"http://{self.ip_address}:{self.port}/"
        self.thread = None
        self.start_thread()  # Start the thread to run the scatter plot

    def create_scatter_fig(self):
        # Create a scatter plot figure with custom data for images
        fig = px.scatter(
            data_frame=self.df,
            x=self.x,
            y=self.y,
            custom_data=["img_file_name"]
        )
        fig.update_traces(marker=dict(size=10, color='#a3a7e4'), hoverinfo='none', hovertemplate=None)

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=list([
                        dict(label="Linear",
                             method="relayout",
                             args=[{"yaxis.type": "linear"}]
                             ),
                        dict(label="Log",
                             method="relayout",
                             args=[{"yaxis.type": "log"}]
                             )
                    ]),
                    type="buttons",
                    direction="down",
                    showactive=True,
                    x=-0.03,
                    xanchor="left",
                    y=1,
                    yanchor="top"
                ),
                dict(
                    buttons=list([
                        dict(label="Linear",
                             method="relayout",
                             args=[{"xaxis.type": "linear"}]
                             ),
                        dict(label="Log",
                             method="relayout",
                             args=[{"xaxis.type": "log"}]
                             )
                    ]),
                    type="buttons",
                    direction="right",
                    showactive=True,
                    x=0.90,
                    xanchor="left",
                    y=-0.05,
                    yanchor="top"
                ),
                dict(
                    buttons=list([
                        dict(label="Linear",
                             method="relayout",
                             args=[{"yaxis.type": "linear"}]
                             ),
                        dict(label="Log",
                             method="relayout",
                             args=[{"yaxis.type": "log"}]
                             )
                    ]),
                    type="buttons",
                    direction="down",
                    showactive=True,
                    x=-0.03,
                    xanchor="left",
                    y=1,
                    yanchor="top"
                ),
                dict(
                    buttons=list([
                        dict(label="Linear",
                             method="relayout",
                             args=[{"xaxis.type": "linear"}]
                             ),
                        dict(label="Log",
                             method="relayout",
                             args=[{"xaxis.type": "log"}]
                             )
                    ]),
                    type="buttons",
                    direction="right",
                    showactive=True,
                    x=0.90,
                    xanchor="left",
                    y=-0.05,
                    yanchor="top"
                ),
            ]
        )
        return fig  # Return the created figure

    def scatter_plot(self):
        fig = self.create_scatter_fig()  # Create scatter plot figure

        app = Dash(__name__)

        app.layout = html.Div([
            dcc.Graph(id='scatter-plot', figure=fig, clear_on_unhover=True),
            dcc.Tooltip(id="graph-tooltip-2", direction='bottom'),
            html.Button('X', id='stop-button', n_clicks=0,
                        style={'position': 'absolute', 'top': 10, 'right': 10,
                               'background-color': 'red', 'color': 'white'})
        ],
            style={'position': 'relative', 'width': '100%', 'height': '100%'}
        )

        @callback(
            Output('stop-button', 'children'),
            Input('stop-button', 'n_clicks')
        )
        def stop_server(n_clicks):
            # Stop the server if the stop button is clicked
            if n_clicks:
                self.stop_thread()
                return "Server stopped"
            return "X"

        @callback(
            Output("graph-tooltip-2", "show"),
            Output("graph-tooltip-2", "bbox"),
            Output("graph-tooltip-2", "children"),
            Output("graph-tooltip-2", "direction"),
            Input("scatter-plot", "hoverData"), 
        )
        def display_hover(hoverData):
            # Display the tooltip with image on hover
            if not self.done:
                self.done = True

            if hoverData is None:
                print("No hover data")
                return False, no_update, no_update, no_update

            pt = hoverData["points"][0]
            img_file_name = pt["customdata"][0]
            print(f"Hover data received: {img_file_name}")

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

        app.run(debug=False, host=self.ip_address, port=self.port, use_reloader=False)
        print(f"Server running at {self.url}")

    def start_thread(self):
        # Start the scatter plot in a separate thread
        self.thread = utils.ControlledThread(target=self.scatter_plot)
        self.thread.start()

    def stop_thread(self):
        # Stop the running thread
        msg = {"command": "remove iframe", "src": self.url}
        self.controller.publish(self.publisher, json.dumps(msg))
        self.thread.kill()
        self.thread.join()
        print("Server stopped at", self.url)

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
