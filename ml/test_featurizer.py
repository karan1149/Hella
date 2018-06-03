import pickle
import sys
import time
import argparse

from sklearn import utils

sys.path.insert(0, '..')

from featurizer import *

def test_CBF(packets):
    print('Test CountBasedFeaturizer')
    CBF = CountBasedFeaturizer(50)
    pkts_read = 0
    featurized_packets = []        
    for packet in packets:
        feats = CBF.featurize(packet)        
        utils.validation.assert_all_finite(feats)
        featurized_packets.append(feats)        
        pkts_read += 1
        if pkts_read > CBF.pkt_window * 2:
            break    
    print('done')                   

def test_TBF(packets):
    print('Test TimeBasedFeaturizer')
    TBF = TimeBasedFeaturizer(1)
    start = time.time()
    featurized_packets = []    
    for packet in packets:
        feats = TBF.featurize(packet)
        utils.validation.assert_all_finite(feats)
        featurized_packets.append(feats)
        if time.time() - start > TBF.sec_window * 2:
            break
    print('done')            

def test_BF(packets):
    print("Test BasicFeaturizer")
    BF = BasicFeaturizer()
    pkts_read = 0
    featurized_packets = []
    for packet in packets:
        cur_len = -1
        if IP in packet:
            feats = BF.featurize(packet)
            assert(cur_len == -1 or cur_len == len(feats))
            cur_len = len(feats)
            assert(feats[2] == 1)
            if UDP in packet:
                assert(feats[1] == 0)
            elif TCP in packet:
                assert(feats[1] == 1)
            else:
                assert(feats[1] == 0)          
        else: 
            feats = BF.featurize(packet)
            assert(feats[2] == 0)
        utils.validation.assert_all_finite(feats)
        featurized_packets.append(feats)
        pkts_read += 1
        if pkts_read > 10000:
            break
    print('done')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_file', help='the .pkl file to read packet data from')
    args = parser.parse_args()

    with open(args.data_file, 'rb') as data_file:
        packets = pickle.load(data_file)
    test_CBF(packets)
    test_TBF(packets)
    test_BF(packets)