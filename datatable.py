import plotly.express as px
from dash import Dash, dash_table, dcc, html, Input, Output, State, callback_context
import numpy as np
import pandas as pd
import threading

class DataTable:
    def __init__(self, controller, app, df=None):
        # Initialize the DataTable with a controller, Dash app, and optional DataFrame
        self.df_parent = df if df is not None else pd.DataFrame()
        self.controller = controller
        self.app = app
        self.publisher = "visualization/datatable"

        # Define default rows for the table
        self.default_rows = [
            "object_width",
            "object_height",
            "object_area",
            "object_elongation",
            "object_circex"
        ]

        # Define default columns for the table
        self.default_columns = [
            "mean",
            "min",
            "max",
            "sd"
        ]

        # Map statistical operations to their corresponding methods
        self.stats_operations = {
            'mean': self.mean,
            'sd': self.sd,
            'min': self.min,
            'max': self.max
        }

        # Create the default DataFrame and table layout
        self.df = self.create_default_df()
        self.create_table()

    def create_default_df(self):
        # Create a default DataFrame with the defined rows and columns
        data = {'Morphology metrics': self.default_rows}
        for col in self.default_columns:
            data[col] = [0.00] * len(self.default_rows)  # Initialize with zeros
        return pd.DataFrame(data)
    
    def reset_df(self):
        # Reset the DataFrame to the default state
        self.df = self.create_default_df()

    def load_df(self, df):
        # Load a new DataFrame and update the table
        self.df_parent = df

        for row_index, row in enumerate(self.df.iterrows()):
            metadata = self.df["Morphology metrics"][row_index]
            for col_index, (column, value) in enumerate(row[1].items()):
                if column in self.stats_operations:
                    self.df.loc[row_index, column] = self.stats_operations[column](metadata)

    def get_options(self):
        # Get the options for the dropdown menu
        return [{'label': col, 'value': col} for col in self.df_parent.columns if pd.api.types.is_numeric_dtype(self.df_parent[col])]


    def create_layout(self):
        # Create the layout for the Dash app
        self.metadatas_options = self.get_options()

        self.data_table = dash_table.DataTable(
            id='data-table',
            data=self.df.to_dict('records'),
            columns=[{
                'name': col,
                'id': col,
                'deletable': True,
                'renamable': False
            } for col in self.df.columns],
            editable=False,
            row_deletable=True,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center'},
            style_header={'backgroundColor': 'lightgray', 'fontWeight': 'bold'},
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(240, 240, 240)'
            }],
            style_as_list_view=True
        )

        layout = html.Div([
            dcc.Interval(id='interval', interval=2500, n_intervals=0),  # Refresh the table every 2.5 seconds
            html.Div([
                html.Div([self.data_table], style={'flex': 3}),
            ], style={'display': 'flex', 
                      'flex-direction': 'horizontal', 
                      'width': '100%'}
                      ),
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
                    style={'flex': 1,
                           'height': '90%'
                           }
                )
            ], style={'display': 'flex', 
                      'justify-content': 'flex-start', 
                      'align-items': 'center', 
                      'height': 50, 'width': 'auto'}
                      ),
        ], style={'width': '100%', 'height': "100%"})

        return layout

    def create_table(self):
        # Set the layout for the Dash app and define callbacks
        self.app.layout = self.create_layout()

        @self.app.callback(
            [Output('data-table', 'data', allow_duplicate=True),
             Output('adding-rows-dropdown', 'options', allow_duplicate=True)],
            [Input('interval', 'n_intervals')],
            prevent_initial_call=True
        )
        def update_rows(n_intervals):
            # Update the rows and options for the table
            rows = self.df.to_dict('records')
            options = self.get_options()
            return rows, options

        @self.app.callback(
            [Output('data-table', 'columns'), 
             Output('data-table', 'data'), 
             Output('adding-rows-dropdown', 'options')],
            [Input('adding-rows-button', 'n_clicks')],
            [State('data-table', 'data'),
             State('data-table', 'columns'),
             State('adding-rows-dropdown', 'value')]
        )
        def update_table(n_clicks_add_row, rows, columns, row_to_add):
            # Update the table when a new row is added
            trigger = callback_context.triggered[0]['prop_id'].split('.')[0]
            print(f"Trigger: {trigger}")

            if trigger == 'adding-rows-button' and n_clicks_add_row > 0 and row_to_add is not None:
                new_row = {'Morphology metrics': row_to_add}
                for col in columns:
                    if col['id'] != 'Morphology metrics':
                        new_row[col['id']] = self.stats_operations[col['id']](row_to_add) if col['id'] in self.stats_operations else None
                rows.append(new_row)
                options = self.get_options()
                
                # Adding to the df
                self.df = pd.DataFrame(rows)

                return columns, rows, options

            return columns, rows, self.metadatas_options

        @self.app.callback(
            Input('data-table', 'data_previous'),
            State('data-table', 'data')
        )
        def delete_row(previous, current):
            if previous:
                # Update DataFrame to match the current state of the DataTable
                self.df = pd.DataFrame(current)

    def mean(self, col):
        # Calculate the mean of a column
        if not (self.df_parent[col].dtype in [np.float64, np.int64]):
            try:
                return round(np.mean(self.df_parent[col].astype(float)), 2)
            except ValueError:
                return 0
        return round(np.mean(self.df_parent[col]), 2)

    def sd(self, col):
        # Calculate the standard deviation of a column
        if not (self.df_parent[col].dtype in [np.float64, np.int64]):
            try:
                return round(np.std(self.df_parent[col].astype(float)), 2)
            except ValueError:
                return 0
        return round(np.std(self.df_parent[col]), 2)

    def min(self, col):
        # Calculate the minimum value of a column
        if not (self.df_parent[col].dtype in [np.float64, np.int64]):
            try:
                return round(np.min(self.df_parent[col].astype(float)), 2)
            except ValueError:
                return 0
        return round(np.min(self.df_parent[col]), 2)

    def max(self, col):
        # Calculate the maximum value of a column
        if not (self.df_parent[col].dtype in [np.float64, np.int64]):
            try:
                return round(np.max(self.df_parent[col].astype(float)), 2)
            except ValueError:
                return 0
        return round(np.max(self.df_parent[col]), 2)

if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    import threading

    # Generate a toy DataFrame
    data = {
        "object_width": np.random.randint(1, 100, size=10),
        "object_height": np.random.randint(1, 100, size=10),
        "object_area": np.random.randint(1, 1000, size=10),
        "object_elongation": np.random.uniform(0.5, 2.0, size=10),
        "object_circex": np.random.uniform(0.1, 1.0, size=10)
    }

    df = pd.DataFrame(data)

    # Create a Dash app and run it in a separate thread
    app = Dash(__name__)
    app_thread = threading.Thread(target=app.run, args=("localhost", 8050), kwargs={"use_reloader": False, "debug": True}, daemon=True)
    app_thread.start()

    # Create a DataTable instance and load the DataFrame
    data_table = DataTable(None, app)
    input("Press Enter to load the DataFrame")
    data_table.load_df(df)
    input("Press Enter to exit")
    exit()
