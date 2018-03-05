import sklearn
from sklearn.externals import joblib
import sklearn.metrics as metrics
import numpy as np
DEBUG = True

class AnomalyModel(object):
  def __init__(self):
    """
    """
    self.model = sklearn.ensemble.IsolationForest()

  def predict(self, packet):
    """
    Predicts whether the given packet is anomalous.
    Dimensionality of packet is (n_features), +1 if inlier, -1 if anomaly
    """
    return self.model.predict([packet])[0]


  def predicts(self, packets):
    """
    Predicts whether multiple packets are anomalous.
    Dimensionality of packets is (n_samples, n_features).
    Returns predictions with dims (n_samples)
    +1 if inlier, -1 if anomaly
    """
    return self.model.predict(packets)


  def fit(self, packets):
    """
    Trains the underlying model using an unlabeled list of packets.
    Packets has dimensionality (n_samples, n_features)
    """
    self.model.fit(packets)

  def validation(self, packets, labels):
    """
    Takes a list of packets and a list of labels and computes validation scores
    for the trained model.
    - accuracy
    - precision
    - recall
    - f1 score
    - confusion matrix
    """
    predictions = self.model.predict(packets)
    
    accuracy = metrics.accuracy_score(labels, predictions)
    recall = metrics.recall_score(labels, predictions, pos_label=-1)
    precision = metrics.precision_score(labels, predictions, pos_label=-1)
    f1 = 2 * recall * precision / float(recall + precision)
    confusion = metrics.confusion_matrix(labels, predictions, labels=[1, -1])
    return accuracy, recall, precision, f1, confusion

  def save(self, path):
    """
    Dumps the model to the given path.
    """
    joblib.dump(self.model, path)

  def load(self, path):
    """
    Loads a model dump from path and initializes class members.
    """
    self.model = joblib.load(path)
