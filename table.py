import pandas as pd
import plotly.express as px
from dash import Dash, dash_table, dcc, html, Input, Output, State, callback
import numpy as np
import utils as utils

# Exemple de DataFrame
df = pd.DataFrame({
    'Index': [f'metadata {i+1}' for i in range(10)],  # Ajout des noms de lignes
    'Stat1': np.random.rand(10),
    'Stat2': np.random.rand(10),
    'Stat3': np.random.rand(10),
    'Stat4': np.random.rand(10)
})

stats_options= [{'label': 'Mean', 'value': 'mean'},
                         {'label': 'Standard Deviation', 'value': 'sd'}]

metadatas_options=[]
for col in df.columns:
    if col != 'Index':
        metadatas_options.append({'label': col, 'value': col})



app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            dash_table.DataTable(
                id='data-table',
                columns=[{
                    'name': col,
                    'id': col,
                    'deletable': True,
                    'renamable': True
                } for col in df.columns],
                data=df.to_dict('records'),
                editable=True,
                row_deletable=True
            )
        ], style={'flex': 2}),
        html.Div([
            dcc.Dropdown(
                id='adding-columns-dropdown',
                options=stats_options,
                style={'flex': 2}
            ),
            html.Button('Add Column', id='adding-columns-button', n_clicks=0)
        ], style={'width': '10%', 'display': 'flex', 'flex': 1, 'justify-content': 'flex-start',
                  'height': 50, 'background-color': 'lightgreen'})
    ], style={'display': 'flex', 'width': '100%', 'background-color': 'lightgray'}),

    html.Div([
        dcc.Dropdown(
            id='adding-rows-dropdown',
            options=metadatas_options,
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
def add_row(n_clicks,row_to_add, rows, columns):
    if n_clicks > 0:
        new_row = {c['id']: '' for c in columns}
        new_row['Index'] = row_to_add 
        rows.append(new_row)
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
