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
    #
    html.Div([
        dcc.Dropdown(
            id='column-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns],
            placeholder='Select a column to add a row from...',
            style={'padding': 10}
        ),
        html.Button('Add Row', id='adding-row-button', n_clicks=0)
    ], 
    style={'height': 50,'width': 100,'grid-column':'1/2','grid-row':'2/3','display':'flex','justify-content':'center','align-items':'center',
            'background-color':'#f0f0f0','border-radius':'10px','padding':'10px'}
    ),

    html.Div([
        dcc.Dropdown(
            id='stat-dropdown',
            options=[
                {'label': 'Mean', 'value': 'mean'},
                {'label': 'Standard Deviation', 'value': 'std'}
            ],
            placeholder='Select a statistic to add as column...',
            style={'padding': 10}
        ),
        html.Button('Add Column', id='adding-column-button', n_clicks=0)
    ], 
    style={'height': 50,'width': 100,'grid-column':'2/3','grid-row':'1/2','display':'flex','justify-content':'center','align-items':'center',
            'background-color':'#f0f0f0','border-radius':'10px','padding':'10px'}
    ),
    html.Div([
        dash_table.DataTable(
            id='dynamic-table',
            columns=[{
                'name': col,
                'id': col,
                'deletable': True,
                'renamable': True
            } for col in df.columns],
            data=df.to_dict('records'),
            editable=True,
            row_deletable=True,
            )
        ],
    style={'height': 400,'width': 1000, 'overflowY': 'scroll','overflowX': 'scroll',
            'grid-column': '1 / 2','grid-row': '1 / 2','display':'flex','justify-content':'center','align-items':'center'
            ,'background-color':'#f0f0f0','border-radius':'10px','padding':'10px'}
    )
],
    style={"display":"grid","grid-template-columns":"auto auto","grid-template-rows":"auto auto","gap":"10px"}
)


@callback(
    Output('dynamic-table', 'data'),
    Input('adding-row-button', 'n_clicks'),
    State('column-dropdown', 'value'),
    State('dynamic-table', 'data'),
    State('dynamic-table', 'columns'))
def add_row(n_clicks, selected_column, rows, columns):
    if n_clicks > 0 and selected_column:
        new_row = {c['id']: '' for c in columns}
        new_row[selected_column] = df[selected_column].iloc[len(rows) % len(df[selected_column])]
        rows.append(new_row)
    return rows


@callback(
    Output('dynamic-table', 'columns'),
    Input('adding-column-button', 'n_clicks'),
    State('stat-dropdown', 'value'),
    State('dynamic-table', 'columns'))
def add_column(n_clicks, selected_stat, existing_columns):
    if n_clicks > 0 and selected_stat:
        stat_col_id = f'{selected_stat}'
        if selected_stat == 'mean':
            stat_values = df.mean()
        elif selected_stat == 'std':
            stat_values = df.std()
        existing_columns.append({
            'id': stat_col_id, 'name': stat_col_id,
            'renamable': True, 'deletable': True
        })
        for row in rows:
            row[stat_col_id] = stat_values
    return existing_columns


if __name__ == '__main__':
    port = utils.find_first_available_local_port()
    app.run(debug=True, port=port, use_reloader=False)
