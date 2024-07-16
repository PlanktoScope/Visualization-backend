import paho.mqtt.client as mqtt
import json
import time

# Import custom modules for data loading and plotting
from flask_server import FlaskServer
import load_dataframe as ld
import scatter_plot as sp
import hist_plot as hp
import datatable_plot as dp
import world_map as wm
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
    def __init__(self, broker="localhost", mqtt_port=1883, flask_host="127.0.0.1", flask_port=5000, subscriber="visualization/commands"):
        self.broker = broker  # MQTT broker address
        self.mqtt_port = mqtt_port  # MQTT broker port
        self.flask_host = flask_host
        self.flask_port = flask_port
        self.subscriber = subscriber  # MQTT topic to subscribe to for commands
        self.df = None  # Placeholder for the dataframe
        self.data_table = None  # Placeholder for the data table visualization

        # Initialize MQTT client and set callback functions
        self.controller = mqtt.Client()
        self.controller.on_connect = self.on_connect
        self.controller.on_message = self.on_message
        self.controller.on_publish = self.on_publish

        # Create The Flask server
        self.server = FlaskServer(size=20)

    def on_connect(self, controller, userdata, flags, rc):
        # Callback function when the client connects to the broker
        print("Connected with result code " + str(rc))
        controller.subscribe(self.subscriber)  # Subscribe to the specified topic

    def on_message(self, controller, userdata, received_message):
        # Callback function when a message is received
        try:
            # Parse the received message
            message = json.loads(received_message.payload.decode())
            command = message.get("command")
            args = message.get("args", [])

            print(f"Received command: command:{command}, args:{args}")
            
            app = self.server.get_available_app()

            if command == "load dataframe":
                if len(args) != 1:
                    print(f"Invalid arguments for 'load dataframe': {args}\nExample: {{'command': 'load dataframe', 'args': ['/path/to/dataframe']}}")
                else:
                    # Load dataframe and extract metadata
                    self.df, number_of_object, metadatas_of_interest = ld.load_dataframe(args[0])

                    # Publish metadata and number of objects
                    self.msg = {"command": "add metadata", "metadata": metadatas_of_interest}
                    controller.publish("visualization/chartPage", json.dumps(self.msg))
                    self.msg = str(number_of_object)
                    controller.publish("visualization/numberOfObject", json.dumps(self.msg))
                    print(f"DataFrame loaded from {args[0]}")
            
            elif command == "create scatter plot":
                if len(args) != 2:
                    print(f"Invalid arguments for 'create scatter plot': {args}\nExample: {{'command': 'create scatter plot', 'args': ['x', 'y']}}")
                else:
                    # Create a scatter plot with specified x and y columns
                    x, y = args
                    sp.ScatterPlot(controller, app, self.df, x, y)
                    self.msg = {"command": "add iframe", "src": f"http://{self.flask_host}:{self.flask_port}{app.get_relative_path('/')}"}
                    controller.publish("visualization/chartPage", json.dumps(self.msg))
                    print(f"Scatter plot created with x={x} and y={y}")

            elif command == "create hist plot":
                if len(args) != 1:
                    print(f"Invalid arguments for 'create hist plot': {args}\nExample: {{'command': 'create hist plot', 'args': ['x']}}")
                else:
                    # Create a histogram plot for the specified column
                    x = args[0]
                    hp.HistPlot(controller,app, self.df, x)
                    self.msg = {"command": "add iframe", "src": f"http://{self.flask_host}:{self.flask_port}{app.get_relative_path('/')}"}
                    controller.publish("visualization/chartPage", json.dumps(self.msg))
                    print(f"Histogram plot created for {x}")

            elif command == "init datatable":
                if len(args) != 0:
                    print(f"Invalid arguments for 'initialize datatable plot': {args}\nExample: {{'command': 'initialize datatable plot', 'args': []}}")
                else:
                    # Initialize the data table
                    self.data_table = dp.DataTable(controller,app)
                    self.msg = {"command": "add iframe", "src": f"http://{self.flask_host}:{self.flask_port}{app.get_relative_path('/')}"}
                    controller.publish("visualization/datatable", json.dumps(self.msg))
                    print(f"Datatable created")

            elif command == "create world map":
                if len(args) != 0:
                    print(f"Invalid arguments for 'create world map': {args}\nExample: {{'command': 'create world map', 'args': []}}")
                else:
                    # Create a world map visualization
                    plot = wm.WorldMap(controller,app)
                    self.msg = {"command": "add iframe", "src": f"http://{self.flask_host}:{self.flask_port}{app.get_relative_path('/')}"}
                    controller.publish("visualization/worldmap", json.dumps(self.msg))
                    print(f"World map created")

            else:
                print(f"Unknown command: {command}")

        except json.JSONDecodeError:
            print("JSON decoding error. Message ignored.")
        except Exception as e:
            print(f"Error processing command: {e}")

        

    def on_publish(self, controller, userdata, mid):
        # Callback function when a message is published
        print("Message: ", self.msg, " sent")

    def run(self):
        # Connect to the MQTT broker and start listening for messages
        try:
            self.controller.connect(self.broker, self.mqtt_port, 60)
            self.controller_thread = utils.ControlledThread(target=self.controller.loop_forever)
            self.server_thread = utils.ControlledThread(target=self.server.run, kwargs={"debug": True, "use_reloader": False,
                                                                                        "host": self.flask_host, "port": self.flask_port})
            self.controller_thread.start()
            self.server_thread.start()
        except Exception as e:
            print(f"Failed to start: {e}")

if __name__ == "__main__":
    # Create an instance of the visualization controller and run it
    visualization_controller = VisualizationController()
    visualization_controller.run()