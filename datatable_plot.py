import plotly.express as px
from dash import Dash, dash_table, dcc, html, Input, Output, State, callback_context, callback
import numpy as np
import json
import utils as utils
import pandas as pd

class DataTable:
    def __init__(self, controller, df=utils.CustomDataFrame()):
        self.df_parent = df
        self.controller = controller
        self.publisher = "visualization/datatable"
        self.port = utils.find_first_available_local_port()
        self.ip_address = utils.get_raspberry_pi_ip()
        self.url = f"http://{self.ip_address}:{self.port}/"
        self.thread = None

        self.default_rows = [
            "object_width",
            "object_height",
            "object_area",
            "object_elongation",
            "object_circex"
        ]

        self.default_columns = [
            "mean",
            "min",
            "max",
            "sd"
        ]

        self.stats_operations = {
            'mean': self.mean,
            'sd': self.sd,
            'min': self.min,
            'max': self.max
        }

        self.df = self.create_default_df()
        self.start_thread()

    def create_default_df(self):
        data = {'Index': self.default_rows}
        for col in self.default_columns:
            data[col] = [0] * len(self.default_rows)  # Initialize with zeros
        return pd.DataFrame(data)

    def load_df(self, df):
        self.df_parent = df

        for row_index, row in enumerate(self.df.iterrows()):
            metadata = self.df["Index"][row_index]
            for col_index, (column, value) in enumerate(row[1].items()):
                if column in self.stats_operations:
                    self.df.loc[row_index, column] = self.stats_operations[column](metadata)
        
        self.app.layout = self.create_layout()

        print(self.df)


    def create_layout(self):

        self.metadatas_options = [{'label': col, 'value': col} for col in self.df_parent.columns if col != 'Index']

        self.data_table = dash_table.DataTable(
            id='data-table',
            data=self.df.to_dict('records'),
            columns=[{
                'name': col,
                'id': col,
                'deletable': True,
                'renamable': True
            } for col in self.df.columns],
            editable=True,
            row_deletable=True,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center'},
            style_header={'backgroundColor': 'lightgray', 'fontWeight': 'bold'},
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }],
            style_as_list_view=True
        )

        layout = html.Div([
            html.Div([
                html.Div([self.data_table], style={'flex': 3}),
            ], style={'display': 'flex', 'flex-direction': 'horizontal', 'width': '100%', 'background-color': 'lightgray'}),

            html.Div([
                dcc.Dropdown(
                    id='adding-rows-dropdown',
                    options=self.metadatas_options,
                    style={'flex': 2}
                ),
                html.Button('Add Row', id='adding-rows-button', n_clicks=0)
            ], style={'display': 'flex', 'justify-content': 'flex-start', 'align-items': 'center', 'height': 50, 'width': '20%',
                      'background-color': 'lightblue'}),
        ], style={'width': '100%', 'height': "100%", 'margin': 10})

        return layout

    def create_table(self):
        self.app = Dash(__name__)
        self.app.layout = self.create_layout()


        @self.app.callback(
            [Output('data-table', 'columns'), Output('data-table', 'data'), Output('adding-rows-dropdown', 'options')],
            [Input('adding-rows-button', 'n_clicks'), Input('data-table', 'data'), 
             Input('data-table', 'columns')],
            [State('adding-rows-dropdown', 'value')]
        )
        def update_table(n_clicks_add_row, rows, columns, row_to_add):
            changed_id = [p['prop_id'] for p in callback_context.triggered][0]

            if 'adding-rows-button' in changed_id:
                if n_clicks_add_row > 0 and row_to_add is not None:
                    new_row = {'Index': row_to_add}
                    for col in columns:
                        if col['id'] != 'Index':
                            new_row[col['id']] = self.stats_operations[col['id']](self.df_parent[row_to_add]) if col['id'] in self.stats_operations else None
                    rows.append(new_row)

            options = [{'label': col, 'value': col} for col in self.df_parent.columns if col != 'Index']

            return columns, rows, options

        self.app.run_server(port=self.port, host=self.ip_address, debug=True, use_reloader=False)

    def mean(self, col):
        if not (self.df_parent[col].dtype in [np.float64, np.int64]):   
            return 0
        return round(np.mean(self.df_parent[col]), 2)

    def sd(self, col):
        if not (self.df_parent[col].dtype in [np.float64, np.int64]):
            return 0
        return round(np.std(self.df_parent[col]), 2)

    def min(self, col):
        if not (self.df_parent[col].dtype in [np.float64, np.int64]):
            return 0
        return round(np.min(self.df_parent[col]), 2)

    def max(self, col):
        if not (self.df_parent[col].dtype in [np.float64, np.int64]):
            return 0
        return round(np.max(self.df_parent[col]), 2)

    def start_thread(self):
        self.thread = utils.ControlledThread(target=self.create_table)
        self.thread.start()

    def stop_thread(self):
        msg = {"command": "remove iframe", "src": self.url}
        self.controller.publish(self.publisher, json.dumps(msg))
        self.thread.kill()
        self.thread.join()
        print("Server stopped at", self.url)


if __name__ == '__main__':
    import time
    import pandas as pd
    import numpy as np

    # Generate a toy DataFrame
    data = {
        "object_width": np.random.randint(1, 100, size=10),
        "object_height": np.random.randint(1, 100, size=10),
        "object_area": np.random.randint(1, 1000, size=10),
        "object_elongation": np.random.uniform(0.5, 2.0, size=10),
        "object_circex": np.random.uniform(0.1, 1.0, size=10)
    }

    df = pd.DataFrame(data)
    data_table = DataTable(None)
    time.sleep(1)   
    data_table.load_df(df)
    exit()
