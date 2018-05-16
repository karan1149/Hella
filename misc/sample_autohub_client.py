import requests
import json
import os

API_BASE = "http://seer-autohub.herokuapp.com/api/v1/"
API_KEY = "fill-me" # I'm on the OneNote -> Documentation -> Design -> seer-car-hub


def get_update_info():
  api_url = API_BASE + 'car/updates/list?key=%s' % API_KEY
  response = requests.get(api_url)
  if response.status_code == 401:
    raise Exception("Not authorized.")
  else:
    return json.loads(response.content)

def get_latest_update():
  api_url = API_BASE + 'car/updates/latest?key=%s' % API_KEY
  response = requests.get(api_url)
  if response.status_code == 401:
    raise Exception("Not authorized.")
  else:
    return response.content

def get_update(id_):
  api_url = API_BASE + 'car/update?id=%s&key=%s' % (id_, API_KEY)
  response = requests.get(api_url)
  if response.status_code == 401:
    raise Exception("Not authorized.")
  elif response.status_code == 404:
    raise Exception("Update not found.")
  else:
    return response.content

if __name__ == "__main__":

  # Get JSON of updates available.
  update_info = get_update_info()
  print(get_update_info())

  # Get the latest update tarball and write
  # it to the file latest.update.
  update = get_latest_update()
  with open("latest.update", "wb") as handle:
      handle.write(update)

  # Get specific update tarball and write it
  # to the file specific.update.
  update_id = "7d93e61d-2dd2-4829-ac94-4a6c5edc52d3"
  update = get_update(update_id)
  with open("specific.update", "wb") as handle:
      handle.write(update)
