from flask import Flask

app = Flask(__name__,
            template_folder="templates")

import zoo.views

# TODO: add blueprints