import paho.mqtt.client as mqtt
import json
import time

# Import custom modules for data loading and plotting
import load_dataframe as ld
import scatter_plot as sp
import hist_plot as hp
import datatable_plot as dp
import world_map as wm
import utils as utils

class VisualizationController:
    def __init__(self, broker="localhost", port=1883, subscriber="visualization/commands"):
        self.broker = broker  # MQTT broker address
        self.port = port  # MQTT broker port
        self.subscriber = subscriber  # MQTT topic to subscribe to for commands
        self.df = None  # Placeholder for the dataframe
        self.data_table = None  # Placeholder for the data table visualization

        # Initialize MQTT client and set callback functions
        self.controller = mqtt.Client()
        self.controller.on_connect = self.on_connect
        self.controller.on_message = self.on_message
        self.controller.on_publish = self.on_publish

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

            if command == "load dataframe":
                if len(args) != 1:
                    print(f"Invalid arguments for 'load dataframe': {args}\nExample: {{'command': 'load dataframe', 'args': ['/path/to/dataframe']}}")
                else:
                    # Load dataframe and extract metadata
                    self.df, number_of_object, metadatas_of_interest = ld.load_dataframe(args[0])
                    self.data_table.load_df(self.df)
                    print(f"DataTable loaded")

                    # Publish metadata and number of objects
                    self.msg = {"command": "add metadata", "metadata": metadatas_of_interest}
                    controller.publish("visualization/chartPage", json.dumps(self.msg))
                    self.msg = str(number_of_object)
                    controller.publish("visualization/numberOfObject", json.dumps(self.msg))
                    print(f"DataFrame loaded from {args[0]}")
                    self.create_default_plot(self.df, controller)
            
            elif command == "create scatter plot":
                if len(args) != 2:
                    print(f"Invalid arguments for 'create scatter plot': {args}\nExample: {{'command': 'create scatter plot', 'args': ['x', 'y']}}")
                else:
                    # Create a scatter plot with specified x and y columns
                    x, y = args
                    plot = sp.ScatterPlot(controller, self.df, x, y)
                    time.sleep(0.5)  # Delay to ensure the plot is created
                    self.msg = {"command": "add iframe", "src": plot.url}
                    controller.publish("visualization/chartPage", json.dumps(self.msg))
                    print(f"Scatter plot created with x={x} and y={y}")

            elif command == "create hist plot":
                if len(args) != 1:
                    print(f"Invalid arguments for 'create hist plot': {args}\nExample: {{'command': 'create hist plot', 'args': ['x']}}")
                else:
                    # Create a histogram plot for the specified column
                    x = args[0]
                    plot = hp.HistPlot(controller, self.df, x)
                    time.sleep(0.5)  # Delay to ensure the plot is created
                    self.msg = {"command": "add iframe", "src": plot.url}
                    controller.publish("visualization/chartPage", json.dumps(self.msg))
                    print(f"Histogram plot created for {x}")

            elif command == "init datatable":
                if len(args) != 0:
                    print(f"Invalid arguments for 'initialize datatable plot': {args}\nExample: {{'command': 'initialize datatable plot', 'args': []}}")
                else:
                    # Initialize the data table
                    self.data_table = dp.DataTable(controller)
                    time.sleep(0.5)  # Delay to ensure the data table is initialized
                    self.msg = {"command": "add iframe", "src": self.data_table.url}
                    controller.publish("visualization/datatable", json.dumps(self.msg))
                    print(f"Datatable created")

            elif command == "create world map":
                if len(args) != 0:
                    print(f"Invalid arguments for 'create world map': {args}\nExample: {{'command': 'create world map', 'args': []}}")
                else:
                    # Create a world map visualization
                    plot = wm.WorldMap(controller)
                    time.sleep(1)  # Delay to ensure the plot is created
                    self.msg = {"command": "add iframe", "src": plot.url}
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

    def create_default_plot(self, df, controller):
        # Create default scatter plot if columns exist in dataframe
        default_plots = [("object_width", "object_height"), ("object_bx", "object_by")]

        x, y = default_plots[0]
        if x in df.keys() and y in df.keys():
            plot = sp.ScatterPlot(controller, df, x, y)
            self.msg = {"command": "add iframe", "src": plot.url}
            controller.publish("visualization/chartPage", json.dumps(self.msg))
            print(f"Scatter plot created with x={x} and y={y}")
        else:
            print(f"Could not create scatter plot with x={x} and y={y}")

    def run(self):
        # Connect to the MQTT broker and start listening for messages
        self.controller.connect(self.broker, self.port, 60)
        self.controller.loop_forever()  # Enter the network loop

if __name__ == "__main__":
    # Create an instance of the visualization controller and run it
    visualization_controller = VisualizationController()
    visualization_controller.run()
