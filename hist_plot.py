import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import json

import utils as utils


class HistPlot:
    def __init__(self,controller, df, x):
        self.controller = controller
        self.df = df
        self.x = x

        self.publisher = "visualization/chartPage"
        self.port = utils.find_first_available_local_port()
        self.ip_address=utils.get_raspberry_pi_ip()
        self.url = f"http://{self.ip_address}:{self.port}/"
        self.thread = None
        self.start_thread()

    def create_hist_fig(self):
        # Create a Plotly Express histogram
        fig = px.histogram(data_frame=self.df, x=self.x)

        # Create buttons for standard units and percentages
        normalization_buttons = [
            {
                'label': 'Standard Units',
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
                    'pad': {'r': 10, 't': 10},
                    'showactive': True,
                    'type': 'buttons',
                    'x': 0.1,
                    'xanchor': 'left',
                    'y': 1.1,
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
        

        app = Dash(__name__)

        app.layout = html.Div([
            dcc.Graph(id='hist-plot', figure=fig),
            html.Div(id='output-div'),
            html.Button('X', id='stop-button', n_clicks=0,
                        style={'position': 'absolute', 'top': 10, 'right': 10,
                               'background-color': 'red', 'color': 'white'})
        ],
            style={'position': 'relative', 'width': '100%', 'height': '100%'}
        )

        # @app.callback(
        #     Output('output-div', 'children'),
        #     Input('hist-plot', 'clickData')
        # )
        # def display_click_data(clickData):
        #     if clickData is None:
        #         return "Cliquez sur un point pour voir les données personnalisées"
        #     point_data = clickData['points'][0]
        #     customdata = point_data['customdata']
        #     return f'Clicked point customdata: {customdata}'
        
        @app.callback(
            Output('stop-button', 'children'),
            Input('stop-button', 'n_clicks')
        )
        def stop_server(n_clicks):
            if n_clicks:
                self.stop_thread()
                return "Server stopped"
            return "X"

        app.run_server(debug=False,host=self.ip_address, port=self.port,use_reloader=False)

        print(f"Server running at {self.url}")

    def start_thread(self):
        self.thread = utils.ControlledThread(target=self.hist_plot)
        self.thread.start()

    def stop_thread(self):
        msg= {"command": "remove iframe", "src": self.url}
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


    #hist plot
    hist_plot = HistPlot(df, x, y)

    input("Press Enter to stop the main thread")


