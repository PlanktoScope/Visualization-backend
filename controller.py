import paho.mqtt.client as mqtt
import json
import time
from flask import request
import threading

# Import custom modules for data loading and plotting

from flask_server import FlaskServer
import scatter_plot as sp
import hist_plot as hp
import datatable as dp
import infotable as ip
import world_map as wm
import timeline as tm
import utils as utils


"""
VisualizationController class is a MQTT controller listenning to the visualization/commands topic where Json object transit. 
It also respond to the frontend so it display the plots.

/!\ This table may be not correct !!!

            ***Recieve***                           |           ***Response***
----------------------------------------------------|-----------------------------------------------------------------------------
    -{command : load dataframe, args:[]             |    ->visualization/chartPage : {command:add metadatas, args[m1,m2,m3...] }
                                                    |    ->visualization/numberOfObject : 20
----------------------------------------------------|-----------------------------------------------------------------------------                   
    -{command : create scatter plot, args:[x,y]}    |    ->visualization/chartPage : {command:scatter plot created, args:x,y}
----------------------------------------------------|-----------------------------------------------------------------------------                    
    -{command : create hist plot, args:[x]}         |    ->visualization/chartPage : {command:add iframe, src : http://localhost:5000/plot1}
----------------------------------------------------|-----------------------------------------------------------------------------                    
    -{command : init datatable}                     |    ->visualization/datatable : {command:add iframe, src : http://localhost:5000/plot1}
----------------------------------------------------|-----------------------------------------------------------------------------                    
    -{command : world map}                          |    ->visualization/map : {command:add iframe, src : http://localhost:5000/plot1}
    
"""

class VisualizationController:
    def __init__(self, BROKER="localhost", MQTT_PORT=1883, FLASK_HOST="127.0.0.1", FLASK_PORT=5000, SUBSCRIBER="visualization/commands"):
        self.BROKER = BROKER  # MQTT BROKER address
        self.MQTT_PORT = MQTT_PORT  # MQTT BROKER port
        self.FLASK_HOST = FLASK_HOST
        self.FLASK_PORT = FLASK_PORT
        self.SUBSCRIBER = SUBSCRIBER  # MQTT topic to subscribe to for commands

        self.df = None  # Placeholder for the dataframe
        self.map = None # Placeholder for the map
        self.timeline=None # Placeholder for the timeline
        self.data_table = None  # Placeholder for the data table visualization
        self.info_table = None  # Placeholder for the info table visualization

        self.BASIC_PLOTS = [
            {"type": "hist", "x": "object_equivalent_diameter"},
            {"type": "hist", "x": "object_area"},
            {"type": "scatter", "x": "object_x", "y": "object_y"},
            {"type":"scatter", "x":"object_elongation", "y":"object_meansaturation"}
            ]

        # Initialize MQTT client and set callback functions
        self.controller = mqtt.Client()
        self.controller.on_connect = self.on_connect
        self.controller.on_message = self.on_message
        self.controller.on_publish = self.on_publish

        # Create The Flask server
        self.server = FlaskServer(size=20)


    def on_connect(self, controller, userdata, flags, rc):
        # Callback function when the client connects to the BROKER
        print("Connected with result code " + str(rc))
        controller.subscribe(self.SUBSCRIBER)  # Subscribe to the specified topic

    def on_message(self, controller, userdata, received_message):
        # Callback function when a message is received
        try:
            # Parse the received message
            message = json.loads(received_message.payload.decode())
            command = message.get("command").replace(" ", "_")  # Replace spaces with underscores for method names
            args = message.get("args", [])

            print(f"Received command: command:{command}, args:{args}")
            
            app = self.server.get_available_app()

            # Dynamically call the method corresponding to the command
            method = getattr(self, command, None)
            if method:
                method(controller, app, *args)
            else:
                print(f"Unknown command: {command}")

        except json.JSONDecodeError:
            print("JSON decoding error. Message ignored.")
        except Exception as e:
            print(f"Error processing command: {e}")

    def clear_all(self, controller, app):

        # Reset tables
        if self.data_table is not None:
            self.data_table.reset_df()

        if self.info_table is not None:
            self.info_table.reset_df()

        # Clear all the plots
        for app_id in self.server.apps.keys():
            app = self.server.apps[app_id]
            if(app != self.map.app and app != self.data_table.app and app != self.timeline.app and app != self.info_table.app):
                app.layout = self.server.default_layout
                app.callback_map.clear()
                if app_id in self.server.apps_running:
                    self.server.apps_running.remove(app_id)
                    base_url="http://"+str(self.FLASK_HOST)+":"+str(self.FLASK_PORT)
                    msg={"command":"remove iframe","src":f"{base_url}{app.get_relative_path('')}"}
                    self.controller.publish("visualization/chartPage", json.dumps(msg))
                if app_id not in self.server.apps_available:
                    self.server.apps_available.append(app_id)


        
    def load_dataframe(self, controller, app, filepath):

        # Load dataframe and extract metadata
        self.df, number_of_object, metadatas_of_interest = utils.load_dataframe(filepath)

        # Set values in the data table if it exists
        if self.data_table is not None:
            self.data_table.load_df(self.df)

        # Set values in the info table if it exists
        if self.info_table is not None:
            self.info_table.load_df(self.df)

        # Create default plots
        self.create_defaults_plots(controller)

        # Publish metadata
        self.msg = {"command": "add metadata", "metadata": metadatas_of_interest}
        controller.publish("visualization/chartPage", json.dumps(self.msg))
        print(f"DataFrame loaded from {filepath}")

    def create_scatter_plot(self, controller, app, x, y):
        if not x or not y:
            print(f"Invalid arguments for 'create scatter plot': {[x, y]}\nExample: {{'command': 'create scatter plot', 'args': ['x', 'y']}}")
        else:
            # Create a scatter plot with specified x and y columns
            sp.ScatterPlot(controller, app, self.df, x, y)
            self.msg = {"command": "add iframe", "src": f"http://{self.FLASK_HOST}:{self.FLASK_PORT}{app.get_relative_path('/')}"}
            controller.publish("visualization/chartPage", json.dumps(self.msg))
            print(f"Scatter plot created with x={x} and y={y}")

    def create_hist_plot(self, controller, app, x):
        if not x:
            print(f"Invalid arguments for 'create hist plot': {x}\nExample: {{'command': 'create hist plot', 'args': ['x']}}")
        else:
            # Create a histogram plot for the specified column
            hp.HistPlot(controller, app, self.df, x)
            self.msg = {"command": "add iframe", "src": f"http://{self.FLASK_HOST}:{self.FLASK_PORT}{app.get_relative_path('/')}"}
            controller.publish("visualization/chartPage", json.dumps(self.msg))
            print(f"Histogram plot created for {x}")

    def init_datatable(self, controller, app):
        if(self.data_table is not None):
            app=self.data_table.app
        else:
            # Initialize the data table
            self.data_table = dp.DataTable(controller, app)
        self.msg = {"command": "add iframe", "src": f"http://{self.FLASK_HOST}:{self.FLASK_PORT}{app.get_relative_path('/')}"}
        controller.publish("visualization/datatable", json.dumps(self.msg))
        print(f"Datatable created")

    def init_infotable(self, controller, app):
        if(self.info_table is not None):
            app=self.info_table.app
        else:
            # Initialize the data table
            self.info_table = ip.InfoTable(controller, app)
        self.msg = {"command": "add iframe", "src": f"http://{self.FLASK_HOST}:{self.FLASK_PORT}{app.get_relative_path('/')}"}
        controller.publish("visualization/infotable", json.dumps(self.msg))
        print(f"InfoTable created")

    def create_world_map(self, controller, app):
        # Create a world map visualization
        if(self.map is not None):
            app=self.map.app
        else:
            self.map = wm.WorldMap(controller, app)
        self.msg = {"command": "add iframe", "src": f"http://{self.FLASK_HOST}:{self.FLASK_PORT}{app.get_relative_path('/')}"}
        controller.publish("visualization/worldmap", json.dumps(self.msg))
        print(f"World map created")

    def create_timeline(self,controller,app):

        if(self.timeline is not None):
            app=self.timeline.app
        else:
            self.timeline=tm.Timeline(controller,app)
        self.msg = {"command": "add iframe", "src": f"http://{self.FLASK_HOST}:{self.FLASK_PORT}{app.get_relative_path('/')}"}
        controller.publish("visualization/timeline", json.dumps(self.msg))
        print(f"Timeline created")

    def create_defaults_plots(self, controller):
        for plot in self.BASIC_PLOTS:
            
            if plot["type"] == "scatter":
                try:
                    self.create_scatter_plot(controller, self.server.get_available_app(), plot["x"], plot["y"])
                except Exception as e:
                    print(f"Failed to create scatter plot: {e}")
            elif plot["type"] == "hist":
                try:
                    self.create_hist_plot(controller, self.server.get_available_app(), plot["x"])
                except Exception as e:
                    print(f"Failed to create histogram plot: {e}")

    def on_publish(self, controller, userdata, mid):
        # Callback function when a message is published
        print("Message: ", mid, " sent")

    def run(self):
        # Connect to the MQTT BROKER and start listening for messages
        try:
            self.controller.connect(self.BROKER, self.MQTT_PORT, 60)
            self.controller_thread = threading.Thread(target=self.controller.loop_forever)
            self.server_thread = threading.Thread(target=self.server.run, kwargs={"debug": False, "use_reloader": False,
                                                                                        "host": self.FLASK_HOST, "port": self.FLASK_PORT})
            self.controller_thread.start()
            self.server_thread.start()
        except Exception as e:
            print(f"Failed to start: {e}")


if __name__ == "__main__":
    # Create an instance of the visualization controller and run it
    visualization_controller = VisualizationController()
    visualization_controller.run()
