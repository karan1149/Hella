import os
import pickle
from anomaly_model import AnomalyModel

directory = 'baseline_models/'
# probability the random flip model should label
# malicious
random_malicious_probability = 0.2

if not os.path.exists(directory):
	os.makedirs(directory)

### RANDOM FLIP MODEL
save_dict = {'featurizer':"BasicFeaturizer", 'random':random_malicious_probability, 'model':None}
with open(directory + 'random_model_' + str(random_malicious_probability) + '.pkl', 'wb') as f:
	pickle.dump(save_dict, f)


### 
