from flask import Flask

app = Flask(__name__,
            template_folder="templates")

import autohub.views

# Register Blueprints

from autohub.blueprints.api.controllers import api
from autohub.blueprints.webui.controllers import webui

app.register_blueprint(api, url_prefix='/api/v1')
app.register_blueprint(webui)
