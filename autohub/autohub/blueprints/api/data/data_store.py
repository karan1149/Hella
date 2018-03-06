import json
import os


def get_latest_update_path(api_root):
  updates_loc = os.path.join(api_root, "data/updates")
  with open(os.path.join(updates_loc, 'updateinfo.json')) as updates:
    updates = json.load(updates)
    return os.path.join(updates_loc, '%s/v1.update' % updates[-1]['id'])

def get_update_list(api_root):
  updates_loc = os.path.join(api_root, "data/updates")
  with open(os.path.join(updates_loc, 'updateinfo.json')) as updates:
    updates = json.load(updates)
    return updates

def get_update_path(api_root, update_id):
  updates_loc = os.path.join(api_root, "data/updates")
  with open(os.path.join(updates_loc, 'updateinfo.json')) as updates:
    updates = json.load(updates)
    for update in updates:
      if update['id'] == update_id:
        return os.path.join(updates_loc, '%s/v1.update' % update_id)
  return None
