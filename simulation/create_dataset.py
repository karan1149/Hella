import sys, os
sys.path.append(os.path.expandvars('../monitor'))
sys.path.append(os.path.expandvars('../ml'))

from test_data import Data_point, Test_data
from utils import *
from scapy.all import *

import api

import random
import pickle
import argparse
from csv import DictReader

FUZZ_THRESHOLD = .3 # fuzz 30% of packets

class DatasetGenerator:
    """
    Saves packets to file.
    Deprecated methods dump Test_data objects.
    gen_api_data dumps list of packets
    """

    def __init__(self, data_file, asset_file, is_training):
        self.data_file = data_file
        self.asset_file = asset_file
        self.is_training = is_training
        self.api = api.API()

    def gen_api_data(self):
        assert self.asset_file

        with open(self.asset_file, 'r') as file:
            reader = DictReader(file)
            for coord in reader:
                time = coord['TIME']
                lat = coord['LATITUDE']
                lng = coord['LONGITUDE']
                func = random.choice(api.GOOGLE_LOCATION_FUNCS)
                self.api.perform_get(func(lat, lng))

        pkts = self.api.recv_pkts

        if self.is_training:
            pickle.dump(pkts, open(self.data_file, 'wb')) 
        else:
            test_data = self.fuzz_data(pkts)
            pickle.dump(test_data, open(self.data_file, 'wb'))  

    def fuzz_data(self, pkts):
        data_points = []
        for i in range(len(pkts)):
            if random.random() < FUZZ_THRESHOLD:
                data_points.append(Data_point(fuzz(pkts[i]), malicious=True))
            else:
                data_points.append(Data_point(pkts[i], malicious=False))
        return Test_data(data_points)           

    # Deprecated
    def gen_legacy_data(self, max_packets=200):
        """
        This function is a relic. We are moving away from external data.
        However, we want to move from 
        """
        assert not self.asset_file

        dps = []

        reader = read_tcpdump_file('data/week2_thursday.tcpdump')
        filtered_pkts = filter_pkts(reader, max_packets=max_packets)
        dps.extend([Data_point(pkt, malicious=True) for pkt in filtered_pkts])

        reader = read_tcpdump_file('data/week1_thursday.tcpdump')
        filtered_pkts = filter_pkts(reader, max_packets=max_packets)
        dps.extend([Data_point(pkt, malicious=False) for pkt in filtered_pkts])

        pickle.dump(Test_data(dps), open(self.data_file, 'wb'))

    # Deprecated
    def gen_test_data(self):
        DUMMY_DATA_POINTS = [
            Data_point(Ether(dst='88:88:88:88:88:88', src='66:66:66:66:66:66') / \
                IP(dst='1.1.1.1', src='2.2.2.2', len=5, id=1, chksum=5) / TCP(chksum=5), malicious=True)
        ]
        DUMMY_TEST_DATA = Test_data(DUMMY_DATA_POINTS)
        
        pickle.dump(DUMMY_TEST_DATA, open(self.data_file, 'wb'))

if __name__ == '__main__':
    print('Run like so: sudo python3 dataset_generator.py -h')

    # sudo python3 dataset_generator.py temp.pkl --asset_file ../../lat_lon/assets/asset77.csv 
    parser = argparse.ArgumentParser()

    parser.add_argument('data_file', help='the dataset dest. file')
    parser.add_argument('--asset_file', help='the asset history .csv')

    train_test = parser.add_mutually_exclusive_group(required=True)
    train_test.add_argument('--train', action='store_true', help='will output .pkl of scapy packets')
    train_test.add_argument('--test', action='store_true', help='will output .pkl containing Test_data object')    

    args = parser.parse_args()

    dataset_generator = DatasetGenerator(args.data_file, args.asset_file, args.train)
    dataset_generator.gen_api_data()