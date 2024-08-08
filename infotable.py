import plotly.express as px
from dash import Dash, dash_table, dcc, html, Input, Output, State, callback_context
import numpy as np
import pandas as pd
import threading

class InfoTable:
    def __init__(self, controller, app, df=None):
        # Initialize the InfoTable with a controller, Dash app, and optional DataFrame
        self.df_parent = df if df is not None else pd.DataFrame()
        self.controller = controller
        self.app = app
        self.publisher = "visualization/infotable"

        # Define default rows for the table
        self.default_rows = {
            "Project Name": "sample_project",
            "Number of objects": None,
            "Sample ID": "sample_id",
            "Ship": "sample_ship",
            "Sampling operator": "sample_operator",
            "Sampling gear": "sample_sampling_gear",
            "Concentrated volume (mL)": "sample_concentrated_sample_volume",
            "Total volume (mL)": "sample_total_volume",
            "Dilution factor": "sample_dilution_factor",
            "Acquisition date (UTC)": "acq_local_datetime",
            "Pixel size (um)": "process_pixel"
        }

        # Create the default DataFrame and table layout
        self.df = self.create_default_df()
        self.create_table()

    def create_default_df(self):
        # Create a default DataFrame with the defined rows
        rows_name = self.default_rows.keys()
        data = {row_name: [None] for row_name in rows_name}
        df = pd.DataFrame(data)
        return df.transpose().reset_index().rename(columns={"index": "Project Information", 0: "Value"})
    
    def reset_df(self):
        # Reset the DataFrame to the default state
        self.df = self.create_default_df()

    def load_df(self, df):
        # Load a new DataFrame and update the table
        self.df_parent = df
        self.df = self.create_default_df()

        for row in self.default_rows:
            if row == "Number of objects":
                self.df.loc[self.df['Project Information'] == row, 'Value'] = len(self.df_parent)
            elif self.default_rows[row] in self.df_parent.columns:
                self.df.loc[self.df['Project Information'] == row, 'Value'] = self.df_parent[self.default_rows[row]].values[0]

    def create_layout(self):
        # Create the layout for the Dash app
        self.metadatas_options = [{'label': col, 'value': col} for col in self.df_parent.columns if col != 'Morphology metrics']

        self.data_table = dash_table.DataTable(
            id='info-table',
            data=self.df.to_dict('records'),
            columns=[{
                'name': col,
                'id': col
            } for col in self.df.columns],

            style_table={'overflowX': 'auto', 'overflowY': 'auto'},
            style_cell={'textAlign': 'left', 'padding-left': '10px', 'padding-right': '10px'},
            style_header={'backgroundColor': 'lightgray', 'fontWeight': 'bold'},
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(240, 240, 240)'
            }],
            style_as_list_view=True
        )

        layout = html.Div([
            dcc.Interval(id='interval', interval=2500, n_intervals=0),  # refresh the table every 2.5 seconds
            html.Div([self.data_table], style={'width': '100%'}),
            html.Div([
                dcc.Dropdown(
                    id='adding-rows-dropdown',
                    options=self.metadatas_options,
                    style={'flex': 2}
                ),
                html.Button(
                    'Add Row',
                    id='adding-rows-button',
                    n_clicks=0,
                    style={'flex': 1, 'height': '90%'}
                )
            ], style={'display': 'flex', 'justify-content': 'flex-start', 'align-items': 'center', 'height': 50, 'width': 'auto'})
        ], style={'width': '100%', 'height': "100%"})

        return layout

    def create_table(self):
        # Set the layout for the Dash app and define callbacks
        self.app.layout = self.create_layout()

        @self.app.callback(
            [Output('info-table', 'data', allow_duplicate=True),
             Output('adding-rows-dropdown', 'options', allow_duplicate=True)],
            [Input('interval', 'n_intervals')],
            prevent_initial_call=True
        )
        def update_rows(n_intervals):
            # Update the rows and options for the table
            rows = self.df.to_dict('records')
            options = [{'label': col, 'value': col} for col in self.df_parent.columns if 'sample' in col or 'acq' in col]
            return rows, options

        @self.app.callback(
            [Output('info-table', 'columns'),
             Output('info-table', 'data'),
             Output('adding-rows-dropdown', 'options')],
            [Input('adding-rows-button', 'n_clicks')],
            [State('info-table', 'data'),
             State('info-table', 'columns'),
             State('adding-rows-dropdown', 'value')]
        )
        def update_table(n_clicks_add_row, rows, columns, row_to_add):
            # Update the table when a new row is added
            trigger = callback_context.triggered[0]['prop_id'].split('.')[0]
            print(f"Trigger: {trigger}")

            if trigger == 'adding-rows-button' and n_clicks_add_row > 0 and row_to_add is not None:
                row_name = row_to_add.split('_')[1:]
                row_name = ' '.join(row_name)
                print(self.df_parent[row_to_add])
                new_row = {"Project Information": row_name, "Value": self.df_parent[row_to_add][1] if len(self.df_parent[row_to_add]) >= 1 else None}

                rows.append(new_row)
                options = [{'label': col, 'value': col} for col in self.df_parent.columns if 'sample' in col or 'acq' in col]

                # Adding to the df
                self.df = pd.DataFrame(rows)

                return columns, rows, options

            return columns, rows, self.metadatas_options


if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    import threading

    # Generate a toy DataFrame
    data = {
        "sample_project": ["project1"],
        "sample_id": ["id1"],
        "sample_ship": ["ship1"],
        "sample_operator": ["operator1"],
        "sample_sampling_gear": ["gear1"],
        "sample_concentrated_sample_volume": [1],
        "sample_total_volume": [2],
        "sample_dilution_factor": [3],
        "acq_local_datetime": ["2021-01-01"],
        "process_pixel": [4],
        "acq_test": [5],
        "sample_test": [6]
    }

    df = pd.DataFrame(data)

    # Create a Dash app and run it in a separate thread
    app = Dash(__name__)
    app_thread = threading.Thread(target=app.run, args=("localhost", 8050), kwargs={"use_reloader": False, "debug": True}, daemon=True)
    app_thread.start()

    # Create an InfoTable instance and load the DataFrame
    data_table = InfoTable(None, app)
    input("Press Enter to load the DataFrame")
    data_table.load_df(df)
    input("Press Enter to exit")
    exit()