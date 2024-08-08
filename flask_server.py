from flask import Flask, url_for, request
from dash import Dash, html

class FlaskServer():
    def __init__(self, size=20):
        # Initialize the FlaskServer with a given size (number of Dash apps)
        self.size = size
        self.default_layout = html.Div(id='dash-container', children=[
            html.H1(f"Hello Dash"), html.Br(), html.H2("Nothing running here...")
        ])

        # Initialize server and app containers
        self.server = None
        self.apps = {}
        self.apps_running = []
        self.apps_available = []
        self.init_flask_server()  # Create a Flask server with a number of empty apps defined by self.size

    def init_flask_server(self):
        # Create the Flask server
        self.server = Flask(import_name="Visualization Server")

        # Initialize Dash apps and add them to the server
        for i in range(self.size):
            app = Dash(
                f"app{i}",
                server=self.server,
                url_base_pathname=f'/app{i}/'
            )
            app.layout = self.default_layout
            self.apps[i] = app
            self.apps_available.append(i)

        # Define the root route
        @self.server.route('/')
        def index():
            return 'Hello, Visualization Flask Server!<br> <a href="/apps"> /apps </a>'

        # Define the route to list all apps
        @self.server.route('/apps')
        def list_apps():
            app_links = [
                f'<a href="{url_for("serve_dash_app", app_id=app_id)}">App {app_id} {"Running" if app_id in self.apps_running else ""}</a>'
                for app_id in self.apps.keys()
            ]
            return '<br>'.join(app_links)

        # Define the route to shutdown/reset an app
        # This route is called by the Dash app itself when the close button is clicked
        @self.server.route('/apps/shutdown', methods=['POST'])
        def app_shutdown():
            app_id = request.form.get('app_id', type=int)
            app = self.apps.get(app_id)
            if app:
                app.layout = self.default_layout
                app.callback_map.clear()
                if app_id in self.apps_running:
                    self.apps_running.remove(app_id)
                if app_id not in self.apps_available:
                    self.apps_available.append(app_id)
                return f"App {app_id} has been reset.", 200
            return f"App {app_id} not found.", 404

        # Define the route to serve a specific Dash app
        @self.server.route('/app/<int:app_id>')
        def serve_dash_app(app_id):
            app = self.apps.get(app_id)
            if app:
                return app.index()
            return f"App {app_id} not found.", 404

    def get_available_app(self):
        # Get an available app from the pool
        if not self.apps_available:
            # If no available apps, move the oldest running app to the end of the list
            app = self.apps_running[4]
            self.apps_running.remove(app)
            self.apps_running.append(app)
            return self.apps[app]
            
        i = self.apps_available.pop(0)
        self.apps_running.append(i)
        return self.apps[i]

    def run(self, **kwargs):
        # Run the Flask server with the given arguments
        self.server.run(**kwargs)

if __name__ == "__main__":
    # Create and run the FlaskServer instance
    flask_server = FlaskServer(size=20)
    flask_server.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)