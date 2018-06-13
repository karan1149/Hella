import sklearn
import sklearn.ensemble
from sklearn.ensemble import IsolationForest
from sklearn.externals import joblib
import sklearn.metrics as metrics
import numpy as np
#import matplotlib.pyplot as plt
DEBUG = True
import random

class AnomalyModel(object):
  def __init__(self):
    """
    """
    self.model = IsolationForest()
    self.featurizer = None
    self.random = None

  def predict(self, packet):
    """
    Predicts whether the given packet is anomalous.
    Dimensionality of packet is (n_features), 0 if inlier, 1 if anomaly
    """
    print(packet, len(packet))
    if self.random is None:
        pred = self.model.predict([packet])[0]
        return 1 if pred == -1 else 0
    else:
        if random.random() < self.random:
            return 1
        else:
            return 0

  def predicts(self, packets):
    """
    Predicts whether multiple packets are anomalous.
    Dimensionality of packets is (n_samples, n_features).
    Returns predictions with dims (n_samples)
    0 if inlier, 1 if anomaly
    """
    return [self.predict(pkt) for pkt in packets]


  def fit(self, packets):
    """
    Trains the underlying model using an unlabeled list of packets.
    Packets has dimensionality (n_samples, n_features)
    """
    self.model.fit(packets)

  # Returns tuple of fpr, tpr points for ROC curve, along with area
  # under curve
  def roc_points(self, X, Y):
    if self.random is not None:
        return [0, 0], [0, 0], 0
    predictions = self.model.decision_function(X)
    labels = [-1 if y == 1 else 1 for y in Y] 
    fpr, tpr, thresholds = metrics.roc_curve(labels, predictions)
    return fpr.tolist(), tpr.tolist(), np.trapz(tpr, fpr)

  def validation(self, predictions, labels):
    """
    Takes a list of packets and a list of labels and computes validation scores
    for the trained model.
    - accuracy
    - precision
    - recall
    - f1 score
    - confusion matrix
    """

    accuracy = metrics.accuracy_score(labels, predictions)
    recall = metrics.recall_score(labels, predictions)
    precision = metrics.precision_score(labels, predictions)
    f1 = 2 * recall * precision / float(recall + precision)
    confusion = metrics.confusion_matrix(labels, predictions).tolist()
    return accuracy, recall, precision, f1, confusion

  def save(self, path):
    """
    Dumps the model to the given path.
    """
    joblib.dump({'model': self.model, 'featurizer': self.featurizer, 'random': self.random}, path)

  def load(self, path):
    """
    Loads a model dump from path and initializes class members.
    """
    save_dict = joblib.load(path)
    self.model = save_dict['model']
    self.featurizer = save_dict['featurizer']
    if 'random' in save_dict:
        self.random = save_dict['random']
    else:
        self.random = None
