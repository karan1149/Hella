from flask import Blueprint, render_template, send_file, request, abort, jsonify
from functools import wraps
from .data import data_store

api = Blueprint('api', __name__, template_folder='templates')

# This is clearly just a dummy key for now.
API_KEY = "0279615b-5cb4-4070-abd9-4b9909aca6af"

def require_apikey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if (request.args.get('key') and request.args.get('key') == API_KEY):
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function

@api.route("/car/updates/latest")
@require_apikey
def latest_update():
  path = data_store.get_latest_update_path(api.root_path)
  try:
    return send_file(path, as_attachment=True, attachment_filename='latest.tar')
  except Exception as e:
    return str(e)

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
    return render_template('404.html')

  update_path = data_store.get_update_path(api.root_path, update_id)

  if not update_path:
    return "Update not found."

  try:
    return send_file(update_path, as_attachment=True, attachment_filename='%s.tar' % update_id)
  except Exception as e:
    return "Update not found."

