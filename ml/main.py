from utils import *
from anomaly_model import AnomalyModel

if __name__ == "__main__":
  model = AnomalyModel()
  try:
    model.load('model.pkl')
  except:
    reader = read_tcpdump_file('data/outside.tcpdump')
    packets = [f for f in featurize_packets(reader)]
    model.fit(packets)
    model.save('model.pkl')

  