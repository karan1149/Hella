
DEBUG = True

class AnomalyModel(object):
  def __init__(self):
    """
    """
    pass

  def predict(self, packet):
    """
    Predicts whether the given packet is anomalous.
    """
    pass


  def fit(self, packets):
    """
    Trains the underlying model using an unlabeled list of packets.
    """
    pass

  def validation(self, packets, labels):
    """
    Takes a list of packets and a list of labels and computes validation scores
    for the trained model.
    - accuracy
    - precision
    - f1 score
    - false negative rate
    - false positive rate
    """
    pass

  def save(self, path):
    """
    Dumps the model to the given path.
    """
    pass

  def load(self, path):
    """
    Loads a model dump from path and initializes class members.
    """
    pass
