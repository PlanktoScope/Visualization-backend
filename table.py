import pandas as pd
import plotly.express as px
from dash import Dash, dash_table, dcc, html, Input, Output, State, callback
import numpy as np
import utils as utils

# Exemple de DataFrame
df = pd.DataFrame({
    'A': np.random.rand(10),
    'B': np.random.rand(10),
    'C': np.random.rand(10),
    'D': np.random.rand(10)
})

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            dash_table.DataTable(
                id='data-table',
                columns=[{
                    'name': 'Column {}'.format(i),
                    'id': 'column-{}'.format(i),
                    'deletable': True,
                    'renamable': True
                } for i in range(1, 5)],
                data=[
                    {'column-{}'.format(i): (j + (i-1)*5) for i in range(1, 5)}
                    for j in range(5)
                ],
                editable=True,
                row_deletable=True
            )
        ], style={'flex': 2}),
        html.Div([
            dcc.Dropdown(
                id='adding-columns-dropdown',
                options=[{'label': 'Mean', 'value': 'mean'},
                         {'label': 'Standard Deviation', 'value': 'sd'}],
                style={'flex': 2}
            ),
            html.Button('Add Column', id='adding-columns-button', n_clicks=0,
                        )
        ], style={'width': '10%', 'display': 'flex', 'flex': 1, 'justify-content': 'flex-start',
                    'height':50,'background-color': 'lightgreen'})
    ], style={'display': 'flex', 'width': '100%','background-color': 'lightgray'}),
    
    html.Div([
        dcc.Dropdown(
            id='adding-rows-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns],
            style={'flex': 2}
        ),
        html.Button('Add Row', id='adding-rows-button', n_clicks=0)
    ], style={'display': 'flex', 'justify-content': 'flex-start', 'align-items': 'center', 'height': 50, 'width': '20%',
              'background-color': 'lightblue'}),
])


@callback(
    Output('data-table', 'data'),
    Input('adding-rows-button', 'n_clicks'),
    State('adding-rows-dropdown', 'value'),
    State('data-table', 'data'),
    State('data-table', 'columns'))
def add_row(n_clicks,row_to_add,rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@callback(
    Output('data-table', 'columns'),
    Input('adding-columns-button', 'n_clicks'),
    State('adding-columns-dropdown', 'value'),
    State('data-table', 'data'),
    State('data-table', 'columns'))
def add_column(n_clicks, column_to_add, rows, columns):
    if n_clicks > 0 and column_to_add is not None:
        new_column = {
            'id': column_to_add,
            'name': column_to_add,
            'renamable': True,
            'deletable': True
        }
        columns.append(new_column)
        for row in rows:
            row[column_to_add] = ''
    return columns




if __name__ == '__main__':
    port = utils.find_first_available_local_port()
    app.run(debug=True, port=port, use_reloader=False)
