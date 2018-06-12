import sklearn
import sklearn.ensemble
from sklearn.ensemble import IsolationForest
from sklearn.externals import joblib
import sklearn.metrics as metrics
import numpy as np
import matplotlib.pyplot as plt
DEBUG = True

# Hyperparameters
epochs = 10
batch_size = 50
sequence_length = 4
features = 14
mean_window = 40
loss_tolerance = 2
train_test_split = 8


class ForecastModel(object):
    """
    """
    def __init__(self):
        self.model = self.generate_model()
        self.featurizer = None

    def generate_model(self):

        layers = [
            tf.keras.layers.LSTM(input_shape=(sequence_length - 1, features),
                                 units=32,
                                 return_sequences=True),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(units=128,
                                 return_sequences=True),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(units=100,
                                 return_sequences=False),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(units=features),
            tf.keras.layers.Activation('linear')
        ]
        model = tf.keras.Sequential(layers)
        model.compile(loss='mean_squared_error', optimizer='rmsprop')

        return model

    def prepare_data(self, data, training=True):

        if training:

            print('creating train n-grams...')

            train_grams = []
            for i in range(0, len(data) - sequence_length):
                train_grams.append(data[i: i + sequence_length])
            train_grams = np.array(train_grams)

            print('train data shape : ', train_grams.shape)

            self.x_train = train_grams[:, :-1]
            self.y_train = train_grams[:, -1]

        else:

            print('creating test n-grams...')

            test_grams = []
            for i in range(0, len(data) - sequence_length):
                test_grams.append(data[i: i + sequence_length])
            test_grams = np.array(test_grams)

            print('test data shape : ', test_grams.shape)

            self.x_test = test_grams[:, :-1]
            self.y_test = test_grams[:, -1]

    def fit(self, data):

        self.prepare_data(data)
        self.train_history = self.model.fit(self.x_train, self.y_train,
                                            batch_size=batch_size, epochs=epochs)

    def test(self, data):

        assert self.train_history is not None

        self.prepare_data(data, training=False)

        losses_in_window = deque()
        moving_mean = 0
        rolling_std = 0

        for i in range(self.x_test.shape[0]):

            test_loss = self.model.evaluate(x=np.expand_dims(self.x_test[i], 0),
                                            y=np.expand_dims(self.y_test[i], 0), batch_size=1)

            if i < mean_window:
                moving_mean += test_loss / mean_window
                losses_in_window.append(test_loss)
                print("build mean")
            else:
                moving_mean += (test_loss - losses_in_window[0]) / mean_window
                losses_in_window.popleft()
                losses_in_window.append(test_loss)

                # not efficient
                rolling_std = np.std(losses_in_window)

                if np.abs(test_loss - moving_mean) < rolling_std * loss_tolerance:
                    print("all clear")
                else:
                    print("\nMALICIOUS\n")

  # def predict(self, packet):
  #   """
  #   Predicts whether the given packet is anomalous.
  #   Dimensionality of packet is (n_features), 0 if inlier, 1 if anomaly
  #   """
  #   assert self.train_history is not None
  #   self.prepare_data(data, training=False)
  #   return 1 if pred == -1 else 0


  # def predicts(self, packets):
  #   """
  #   Predicts whether multiple packets are anomalous.
  #   Dimensionality of packets is (n_samples, n_features).
  #   Returns predictions with dims (n_samples)
  #   0 if inlier, 1 if anomaly
  #   """
  #   return [self.predict(pkt) for pkt in packets]


  # Returns tuple of fpr, tpr points for ROC curve, along with area
  # under curve
  def roc_points(self, X, Y):
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
    joblib.dump({'model': self.model, 'featurizer': self.featurizer}, path)

  def load(self, path):
    """
    Loads a model dump from path and initializes class members.
    """
    save_dict = joblib.load(path)
    self.model = save_dict['model']
    self.featurizer = save_dict['featurizer']
