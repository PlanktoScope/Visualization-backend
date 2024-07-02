import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import json
import utils

class ScatterPlot:
    def __init__(self, controller, df, x, y):
        self.controller = controller
        self.df = df
        self.x = x
        self.y = y

        self.publisher = "visualization/chartPage"
        self.port = utils.find_first_available_local_port()
        self.url = f"http://127.0.0.1:{self.port}/"
        self.thread = None
        self.start_thread()
        
    def create_scatter_fig(self):
        fig = px.scatter(
            data_frame=self.df,
            x=self.x,
            y=self.y,
            custom_data=["img_file_name"]
        )
        fig.update_traces(marker=dict(size=10, color='#a3a7e4'))

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
          ]
        )
        return fig

    def scatter_plot(self):
        fig = self.create_scatter_fig()

        app = Dash(__name__)

        app.layout = html.Div([
            dcc.Graph(id='scatter-plot', figure=fig),
            html.Button('X', id='stop-button', n_clicks=0,
                        style={'position': 'absolute', 'top': 10, 'right': 10,
                               'background-color': 'red', 'color': 'white'})
        ],
            style={'position': 'relative', 'width': '100%', 'height': '100%'}
        )

        @app.callback(
            Output('stop-button', 'children'),
            Input('stop-button', 'n_clicks')
        )
        def stop_server(n_clicks):
            if n_clicks:
                self.stop_thread()
                return "Server stopped"
            return "X"


        app.run(debug=False, port=self.port, use_reloader=False)
        print(f"Server running at {self.url}")

    def start_thread(self):
        self.thread = utils.ControlledThread(target=self.scatter_plot)
        self.thread.start()

    def stop_thread(self):
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

    # scatter plot
    scatter_plot = ScatterPlot(None, df, x, y)

    input("Press Enter to stop the main thread")
