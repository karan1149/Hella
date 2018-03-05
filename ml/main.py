from utils import *
from anomaly_model import AnomalyModel

if __name__ == "__main__":
  reader = read_tcpdump_file('data/outside.tcpdump')
  packets = [f for f in featurize_packets(reader)]
  model = AnomalyModel()
  model.fit(packets)

