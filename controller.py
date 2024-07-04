import paho.mqtt.client as mqtt
import json
import time

import load_dataframe as ld
import scatter_plot as sp
import hist_plot as hp
import utils as utils

# Configuration du broker MQTT
broker = "localhost"
port = 1883
subriber = "visualization/commands"
publisher = "visualization/chartPage"

df = None

def on_connect(controller, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    controller.subscribe(subriber)

def on_message(controller, userdata, msg):
    global df
    try:
        message = json.loads(msg.payload.decode())
        command = message.get("command")
        args = message.get("args", [])
        print(f"Commande reçue : {command} {args}")
        print(type(command), type(args))
        
        if command == "load dataframe":
            if len(args) != 1:
                print(f"Arguments invalides pour 'load dataframe': {args}\nExemple: {{'command': 'load dataframe', 'args': ['/path/to/dataframe']}}")
            else:
                df,number_of_object = ld.load_dataframe(args[0])
                msg = {"command": "add metadata", "metadata": df.keys().tolist()}
                controller.publish(publisher, json.dumps(msg))
                msg = str(number_of_object)
                controller.publish("visualization/numberOfObject", json.dumps(msg))
                print(f"DataFrame loaded from {args[0]}")
                create_default_plot(df, controller)        
        elif command == "create scatter plot":
            if len(args) != 2:
                print(f"Arguments invalides pour 'create scatter plot': {args}\nExemple: {{'command': 'create scatter plot', 'args': ['x', 'y']}}")
            else:
                x = args[0]
                y = args[1]
                plot = sp.ScatterPlot(controller,df, x, y)
                time.sleep(0.5)
                msg = {"command": "add iframe", "src": plot.url}
                controller.publish(publisher, json.dumps(msg))
                print(f"Scatter plot created with x={x} and y={y}")
        
        elif command == "create hist plot":
            if len(args) != 1:
                print(f"Arguments invalides pour 'create hist plot': {args}\nExemple: {{'command': 'create hist plot', 'args': ['x']}}")
            else:
                x = args[0]
                plot = hp.HistPlot(controller,df, x)
                time.sleep(0.5)
                msg = {"command": "add iframe", "src": plot.url}
                controller.publish(publisher, json.dumps(msg))
                print(f"Histogram plot created for {x}")

        else:
            print(f"Commande inconnue : {command}")
    
    except json.JSONDecodeError:
        print("Erreur de décodage JSON. Message ignoré.")
    except Exception as e:
        print(f"Erreur lors du traitement de la commande : {e}")

def on_publish(controller, userdata, mid):
    print("Message : ", mid,' ',userdata, " envoyé")

def create_default_plot(df, controller):

    # Create scatter plot width_object -> height_object
    default_plots=[("object_width","object_height"),("object_bx","object_by")]
    for x,y in default_plots:
        if(x in df.keys() and y in df.keys()):
            plot = sp.ScatterPlot(controller,df, x, y)

            msg = {"command": "add iframe", "src": plot.url}
            controller.publish(publisher, json.dumps(msg))
            print(f"Scatter plot created with x={x} and y={y}")

        else:
            print("could not create scatter plot with x={x} and y={y}")
   

if (__name__ == "__main__"):
    
    def run():
        # Initialisation du client MQTT
        controller = mqtt.Client()
        controller.on_connect = on_connect
        controller.on_message = on_message
        controller.on_publish = on_publish

        controller.connect(broker, port, 60)

        # Boucle de réseau pour écouter les messages MQTT
        controller.loop_forever()

    main_thread=utils.ControlledThread(target=run)
    main_thread.start()
    input("Press Enter to stop the main thread")
    main_thread.kill()
    main_thread.join()