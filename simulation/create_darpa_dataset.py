import sys
sys.path.append("./ml")
from utils import *
from anomaly_model import AnomalyModel
sys.path.append("./monitor")
from test_data import Data_point, Test_data
import pickle
from scapy.all import *
import json

def gen_legacy_test_data(data_file, max_packets=200):
        dps = []

        reader = read_scapy_pkts('./ml/data/week2_thursday.tcpdump', max_packets)
        dps.extend([Data_point(pkt, malicious=True) for pkt in reader])

        reader = read_scapy_pkts('./ml/data/week1_thursday.tcpdump', max_packets)
        dps.extend([Data_point(pkt, malicious=False) for pkt in reader])

        pickle.dump(Test_data(dps), open(data_file, 'wb'))


def gen_legacy_train_data(data_file, max_packets=200):
        dps = []

        reader = read_scapy_pkts('./ml/data/week2_thursday.tcpdump', max_packets)
        dps.extend([pkt for pkt in reader])

        reader = read_scapy_pkts('./ml/data/week1_thursday.tcpdump', max_packets)
        dps.extend([pkt for pkt in reader])

        pickle.dump(dps, open(data_file, 'wb'))


if __name__ == '__main__':
    gen_legacy_train_data('darpa_400_py3_train.pkl', 200)
    gen_legacy_test_data('darpa_400_py3.pkl', 200)
