import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import os
import pandas as pd
from flask import request

import utils as utils


class Timeline:
    def __init__(self,controller,app):
        self.controller = controller
        self.app=app

        self.publisher = "visualization/chartPage"

        self.x='date'
        self.y='Objects/ml'

        # Reading data from a JSON file
        data_path = os.path.join('..', 'data', 'summary.json')
        self.df = self.read_data(data_path)

        # Hidding the mode bar
        self.config = {'displayModeBar': False}
        
        self.timeline_plot()

    def read_data(self, filename):
        # Method to load data from a JSON file into a DataFrame
        df = pd.read_json(filename, orient="records")
        
        # Transform the 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'],format='%Y%m%d')
            
        return df

    def create_timeline_fig(self):
        # Create a Plotly Express histogram
        fig = px.bar(data_frame=self.df, x=self.x,y=self.y,barmode='group',color='filename',
                                 hover_data={"filename": True,"date":True,"Objects/ml": ":.2f","lat": True,"lon": True}  # Displaying additional data on hover
)

        # Defining fig height
        fig.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, t=0, b=0),
            height=150,
            width=None,
            showlegend=False           
        )

        fig.update_traces(marker_color='#a3a7e4')

        return fig

    def timeline_plot(self):
        fig = self.create_timeline_fig()

        self.app.layout = html.Div([
            dcc.Graph(id='hist-plot', figure=fig,config=self.config),
            html.Div(id='output-div')          
        ],
            style={'position': 'relative', 'width': '100%', 'height': '100%'}
        )

        
        

# Example usage
if __name__ == "__main__":

    #hist plot
    timeline_plot = Timeline(None,Dash(__name__))



