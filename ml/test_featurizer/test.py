import pickle
import sys
import time

sys.path.insert(0, '..')

from featurizer import *

def test_CBF(packets):
    print('Test CountBasedFeaturizer')
    CBF = CountBasedFeaturizer(50)
    pkts_read = 0
    for packet in packets:
        

    while True:
        pkt_read = reader.__next__()
        raw_pkt = Ether(pkt_read[1])
        if IP in raw_pkt and TCP in raw_pkt:
            feats = CBF.featurize(raw_pkt)
            pkts_read += 1
        if pkts_read > CBF.pkt_window * 2:
            break

def test_TBF(packets):
    print('Test TimeBasedFeaturizer')
    TBF = TimeBasedFeaturizer(1)
    start = time.time()
    while True:
        pkt_read = reader.__next__()
        raw_pkt = Ether(pkt_read[1])
        if IP in raw_pkt and TCP in raw_pkt:
            feats = TBF.featurize(raw_pkt)
        if time.time() - start > TBF.sec_window * 2:
            break

def test_BF():
    print("Test BasicFeaturizer")
    BF = BasicFeaturizer()

    pkts_read = 0
    while True:
        pkt_read = reader.__next__()
        raw_pkt = Ether(pkt_read[1])
        cur_len = -1
        if IP in raw_pkt:
            feats = BF.featurize(raw_pkt)
            assert(cur_len == -1 or cur_len == len(feats))
            cur_len = len(feats)
            assert(feats[2] == 1)
            if UDP in raw_pkt:
                assert(feats[1] == 0)
            elif TCP in raw_pkt:
                assert(feats[1] == 1)
            else:
                assert(feats[1] == 0)          
        else: 
            feats = BF.featurize(raw_pkt)
            assert(feats[2] == 0)
        pkts_read += 1 
        if pkts_read > 10000:
            break

if __name__ == '__main__':
    with open('data.pkl', 'rb') as data_file:
        packets = pickle.load(data_file)
    
    test_CBF(packets)



