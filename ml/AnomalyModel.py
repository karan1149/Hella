import sklearn.ensemble.IsolationForest
from sklearn.externals import joblib
import numpy as np
DEBUG = True

class AnomalyModel(object):
  def __init__(self):
    """
    """
    self.model = IsolationForest()

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
    - false negative rate
    - false positive rate
    """
    predictions = self.model.predict(packets)
    labels = np.array(labels)
    assert(predictions.shape == labels.shape)
    
    accuracy = np.mean(labels == predictions)
    
    

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
