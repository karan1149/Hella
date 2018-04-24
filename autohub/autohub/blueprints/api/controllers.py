import os
import requests
from http import HTTPStatus

from flask import Blueprint, render_template, send_file, request, abort, jsonify
from functools import wraps
from .data import data_store

api = Blueprint('api', __name__, template_folder='templates')

# This is clearly just a dummy key for now.
API_KEY = "0279615b-5cb4-4070-abd9-4b9909aca6af"

# Get Google keys from environment variables.
GOOGLE_GEOCODE_KEY = os.environ['GOOGLE_GEOCODE_KEY']
GOOGLE_PLACES_KEY = os.environ['GOOGLE_PLACES_KEY']

def require_apikey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if (request.args.get('key') and request.args.get('key') == API_KEY):
            return view_function(*args, **kwargs)
        else:
            abort(HTTPStatus.UNAUTHORIZED)
    return decorated_function

@api.route("/car/updates/latest")
@require_apikey
def latest_update():
  path = data_store.get_latest_update_path(api.root_path)
  try:
    return send_file(path, as_attachment=True, attachment_filename='latest.tar')
  except Exception as e:
    return abort(HTTPStatus.INTERNAL_SERVER_ERROR)

@api.route("/car/updates/list")
@require_apikey
def list_updates():
  updates = data_store.get_update_list(api.root_path)
  return jsonify(updates)

@api.route("/car/update")
@require_apikey
def get_update():
  update_id = request.args.get('id')
  if not update_id:
    return abort(HTTPStatus.NOT_FOUND)

  update_path = data_store.get_update_path(api.root_path, update_id)

  if not update_path:
    return abort(HTTPStatus.NOT_FOUND)

  try:
    return send_file(update_path, as_attachment=True, attachment_filename='%s.tar' % update_id)
  except Exception as e:
    return abort(HTTPStatus.NOT_FOUND)

GOOGLE_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json?latlng=%s&key=%s"
@api.route("/car/location/info")
@require_apikey
def get_location_info():
  latlng = request.args.get('latlng')
  if not latlng:
    return abort(HTTPStatus.BAD_REQUEST)

  url = GOOGLE_GEOCODE_URL % (latlng, GOOGLE_GEOCODE_KEY)
  resp = requests.get(url)
  if resp.status_code == requests.codes.ok:
    return jsonify(resp.json())
  else:
    return abort(resp.status_code)

GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s&radius=1000&key=%s"
@api.route("/car/location/nearby")
@require_apikey
def get_nearby_places():
  # Returns nearby places within 1km radius of current location.
  latlng = request.args.get('latlng')
  if not latlng:
    return abort(HTTPStatus.BAD_REQUEST)

  url = GOOGLE_PLACES_URL % (latlng, GOOGLE_PLACES_KEY)
  resp = requests.get(url)
  if resp.status_code == requests.codes.ok:
    return jsonify(resp.json())
  else:
    return abort(resp.status_code)

GOOGLE_PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json?place_id=%s&key=%s"
@api.route("/car/place/details")
@require_apikey
def get_place_details():
  # Returns details about nearby places
  place_id = request.args.get('place_id')
  if not place_id:
    return abort(HTTPStatus.BAD_REQUEST)

  url = GOOGLE_PLACES_DETAILS_URL % (place_id, GOOGLE_PLACES_KEY)
  resp = requests.get(url)
  if resp.status_code == requests.codes.ok:
    return jsonify(resp.json())
  else:
    return abort(resp.status_code)