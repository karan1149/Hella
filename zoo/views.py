import flask
from flask import Flask, jsonify, request, render_template, Response
import os
import sys
sys.path.append("./ml")
from anomaly_model import AnomalyModel
sys.path.append("./monitor")
import test_data
import pickle
from scapy.all import *
import json

dataset_dir = 'zoo/datasets/'
model_dir = 'zoo/models/'

from zoo import app

feat_module = __import__('featurizer')
with open(dataset_dir + "info.json", 'r') as d:
  with open(model_dir + "info.json", 'r') as m:
    datasets_info = json.load(d)
    models_info = json.load(m)

@app.route('/')
def index():
  # Take all files in the appropriate directories matching ".pkl"
  dataset_names = [(make_name_pretty(name), name, datasets_info[name]) for name in os.listdir(dataset_dir) if name.endswith('.pkl')]
  model_names = [(make_name_pretty(name), name, models_info[name]) for name in os.listdir(model_dir) if name.endswith('.pkl')]
  return render_template('index.html', dataset_names=dataset_names, model_names=model_names)

@app.route('/predict', methods=['POST'])
def predict():
  params = request.get_json(silent=True, force=True)
  

  return Response(generate_predictions(params), mimetype='text/plain')


def generate_predictions(params):
  print(params)
  model_path = model_dir + params['model']
  dataset_path = dataset_dir + params['dataset']

  model = AnomalyModel()
  model.load(model_path)

  with open(dataset_path, 'rb') as f:
    test_data = pickle.load(f)

  fr = getattr(feat_module, model.featurizer)()

  X = [fr.featurize(Ether(dp.pkt[1])) for dp in test_data.dps]
  print(len(X))
  Y = [1 if dp.malicious else 0 for dp in test_data.dps]
  num_packets = len(Y)

  start = time.time()
  preds = []
  
  yield json.dumps({"length": len(X)})

  for i, pkt in enumerate(X):
    pred = model.predict(pkt)
    update = {}
    update['label'] = Y[i]
    update['output'] = pred
    yield "\n" + json.dumps(update)
    preds.append(pred)

  diff = time.time() - start
  
  start_roc = time.time()
  fpr, tpr, roc_auc = model.roc_points(X, Y)
  diff_roc = time.time() - start_roc
  print(diff_roc, "Seconds to calculate ROC points and AUC")

  points = zip(fpr, tpr)
  points = [{'x': point[0], 'y': point[1]} for point in points]

  metrics = model.validation(preds, Y)
  
  info = {}
  info['metrics'] = metrics
  info['roc_auc'] = roc_auc
  info['points'] = points
  info['time'] = diff * 1.0 / num_packets
  info['time_total'] = diff

  yield "\n" + json.dumps(info)

# Take a model/dataset name and "prettify" it
# by replacing underscores with spaces and using titlecase
def make_name_pretty(name):
  name = name[:-4]
  name = name.replace("_", " ")
  name = name.title()
  return name
