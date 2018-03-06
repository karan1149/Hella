from flask import Blueprint, render_template, request

webui = Blueprint('webui', __name__, template_folder='templates')

@webui.route("/")
@webui.route("/index")
def home():
  return render_template('index.html')

@webui.route("/coming-soon")
def coming_soon():
  return "<h1> Coming soon :) </h1>"

@webui.route("/about")
def about():
  return render_template("about.html")