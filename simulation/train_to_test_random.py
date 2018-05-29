import sys, os
sys.path.append(os.path.expandvars('../monitor'))
from test_data import Data_point, Test_data
import argparse
import pickle
import random

''' 
Converts a training dataset into a test dataset by randomly labeling some portion as malicious.
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--train_file', help='the .pkl file to read packets from', required=True)
    parser.add_argument('--test_file', help='the .pkl file to write to', required=True)
    parser.add_argument('--contamination', help='The approximate fraction of data that should be randomly labeled malicious, from 0 to 1.', default=0)
    args = parser.parse_args()

    with open(args.train_file, 'rb') as r:
    	packets = pickle.load(r)

    data_points = []
    for pkt in packets:
    	maliciousness = random.random() < float(args.contamination)
    	data_points.append(Data_point(pkt, malicious=maliciousness))
    wrapped_packets = Test_data(data_points)

    with open(args.test_file, 'wb') as w:
    	pickle.dump(wrapped_packets, w)