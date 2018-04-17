import flask
from flask import Flask, jsonify, request, render_template
import os
from anomaly_model import AnomalyModel
import pickle

dataset_dir = 'datasets/'
model_dir = 'models/'

app = Flask(__name__)

@app.route('/')
def index():

	dataset_names = [name[:-4] for name in os.listdir(dataset_dir) if name.endswith('.pkl')]
	model_names = [name[:-4] for name in os.listdir(model_dir) if name.endswith('.pkl')]
	return render_template('index.html', dataset_names=dataset_names, model_names=model_names)

@app.route('/predict', methods=['POST'])
def predict():
	params = request.get_json(silent=True, force=True)
	model_path = model_dir + "isolation_forest.pkl"
	dataset_path = dataset_dir + "darpa_1000.pkl"

	model = AnomalyModel()
	model.load(model_path)

	with open(dataset_path, 'r') as f:
		test_data = pickle.load(f)

	

	return jsonify({})


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug=True)