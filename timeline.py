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

        self.publisher = "visualization/dataset"

        self.x='date'
        self.y='Objects/ml'

        # Reading data from a JSON file
        data_path = os.path.join('..', 'data/export/')
        self.df = self.create_df(data_path)

        # Hidding the mode bar
        self.config = {'displayModeBar': False}
        
        self.timeline_plot()

    def create_df(self, path):
        # Method to create a DataFrame from TSV files in a directory
        columns = ['filename', 'Objects/ml', 'date', 'lat', 'lon']
        df = pd.DataFrame(columns=columns)
        tsvs = utils.find_tsv_files(path)


        # Helper function to extract a value or return a default if not available
        def get_value(df, column, default=1):
            if column in df.columns and not df[column].empty:
                try:
                    value = float(df[column].iloc[0])
                    return value if value else default
                except (ValueError, TypeError):
                    return default
            return default

        data_list = []

        for tsv in tsvs:
            df_temp, nb_objects, metadatas = utils.load_dataframe(tsv)
            
            acq_imaged_volume = get_value(df_temp, "acq_imaged_volume")
            sample_dilution_factor = get_value(df_temp, "sample_dilution_factor")
            sample_concentrated_sample_volume = get_value(df_temp, "sample_concentrated_sample_volume")
            sample_total_volume = get_value(df_temp, "sample_total_volume")

            filename=os.path.basename(tsv)
            filename=filename.split("zip:")[-1]

            data = {
                "filename": filename,
                "Objects/ml": (nb_objects / acq_imaged_volume) * sample_dilution_factor * (sample_concentrated_sample_volume / (sample_total_volume * 1000)),
                "date": df_temp["acq_local_datetime"].iloc[0] if "acq_local_datetime" in df_temp.columns and not df_temp["acq_local_datetime"].empty else None,
                "lat": df_temp["object_lat"].iloc[0] if "object_lat" in df_temp.columns and not df_temp["object_lat"].empty else None,
                "lon": df_temp["object_lon"].iloc[0] if "object_lon" in df_temp.columns and not df_temp["object_lon"].empty else None
            }
            data_list.append(data)

        # delete duplicates
        data_list = [i for n, i in enumerate(data_list) if i not in data_list[n + 1:]]
        
        df = pd.concat([df, pd.DataFrame(data_list)], ignore_index=True)

        
                

        # Transform the 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'])
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')

        return df

    def create_timeline_fig(self):
        # Create a Plotly Express histogram
        fig = px.bar(
                    data_frame=self.df, x=self.x,y=self.y,barmode='group',color='filename',
                    hover_data={"filename": True,"date":True,"Objects/ml": ":.2f","lat": True,"lon": True},  # Displaying additional data on hover
                    custom_data="filename"
                    )

        # Defining fig height
        fig.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, t=0, b=0),
            height=150,
            width=None,
            showlegend=False           
        )
        color=len(self.df)*['#a3a7e4']
        fig.update_traces(marker=dict(color=color))

        return fig

    def timeline_plot(self):
        self.fig = self.create_timeline_fig()

        self.app.layout = html.Div([
            dcc.Graph(id='hist-plot', figure=self.fig,config=self.config),
        ],
            style={'position': 'relative', 'width': '100%', 'height': '100%'}
        )

        #Dataset selection callback
        @self.app.callback(
            Output('hist-plot','figure'),
            Input('hist-plot', 'clickData')
        )
        def select_bar(clickData):
                
            if clickData is not None:

                # Change color of the selected bar
                selected_bar = clickData['points'][0]

                # Updating the figure with the selected bar
                # it doesn t work
                # color = ["#479ef5" if i == selected_bar['curveNumber'] else "#a3a7e4" for i in range(len(self.df))]
                # self.fig.update_traces(marker=dict(color=color))
            
                # Send dataset with MQTT
            
                filename = selected_bar['customdata'][0]
                self.controller.publish(self.publisher, filename)

            return self.fig


        
        

# Example usage
if __name__ == "__main__":

    #hist plot
    timeline_plot = Timeline(None,Dash(__name__))



