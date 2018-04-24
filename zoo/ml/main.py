from utils import *
from anomaly_model import AnomalyModel
import numpy as np

if __name__ == "__main__":
  model = AnomalyModel()
  try:
    model.load('model.pkl')
  except:
    reader = read_tcpdump_file('data/1_monday.tcpdump')
    packets = [f for f in featurize_packets(reader)]
    model.fit(packets)
    pr1 = model.predicts(packets)
    reader = read_tcpdump_file('data/1_tuesday.tcpdump')
    packets = [f for f in featurize_packets(reader)]
    pr2 = model.predicts(packets)
    reader = read_tcpdump_file('data/0_monday.tcpdump')
    packets = [f for f in featurize_packets(reader)]
    pr3 = model.predicts(packets)
    print(np.mean(pr1), np.mean(pr2), np.mean(pr3))
    
  
