from flask import Flask, url_for, request
from dash import Dash, html

class FlaskServer():
    def __init__(self, size=20):
        self.size = size
        self.default_layout = html.Div(id='dash-container', children=[
            html.H1(f"Hello Dash"), html.Br(), html.H2("Nothing running here...")
        ])

        # Creating the Flask server and initializing apps
        self.server = None
        self.apps = {}
        self.apps_running = []
        self.apps_available = []
        self.init_flask_server()  # Create a Flask server with a number of empty apps defined by self.size

    def init_flask_server(self):
        self.server = Flask(import_name="Visualization Server")

        for i in range(self.size):
            app = Dash(
                f"app{i}",
                server=self.server,
                url_base_pathname=f'/app{i}/'
            )
            app.layout = self.default_layout
            self.apps[i] = app
            self.apps_available.append(i)
        @self.server.route('/')
        def index():
            return 'Hello, Visualization Flask Server!<br> <a href="/apps"> /apps </a>'

        @self.server.route('/apps')
        def list_apps():
            app_links = [
                f'<a href="{url_for("serve_dash_app", app_id=app_id)}">App {app_id} {"Running" if app_id in self.apps_running else ""}</a>'
                for app_id in self.apps.keys()
            ]
            return '<br>'.join(app_links)

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

        @self.server.route('/app/<int:app_id>')
        def serve_dash_app(app_id):
            app = self.apps.get(app_id)
            if app:
                return app.index()
            return f"App {app_id} not found.", 404

    def get_available_app(self):
        if not self.apps_available:
            return self.apps[0]
        i = self.apps_available.pop(0)
        self.apps_running.append(i)
        return self.apps[i]

    def run(self, **kwargs):
        self.server.run(**kwargs)

if __name__ == "__main__":
    flask_server = FlaskServer(size=20)
    flask_server.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)
