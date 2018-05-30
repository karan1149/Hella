from collections import deque, defaultdict
from enum import Enum, unique
import scapy
from scapy.all import *
from utils import *

import time

IP_HEADER = ['len', 'id', 'frag', 'ttl', 'proto']
#TCP_HEADER = ['sport', 'dport', 'seq', 'ack', 'flags', 'window']
# edited to remove flags for breakathon
TCP_HEADER = ['sport', 'dport', 'seq', 'ack', 'window']

UDP_HEADER = ['sport', 'dport']

class BasicFeaturizer(object):

    def __init__(self):

        self.BasicFeatures = self._feature_enum()

    def _feature_enum(self):
        """
        Returns an Enum mapping 'time' and all features in IP_HEADER and TCP_HEADER
        to a range of values beginning at 0
        """

        return Enum('Features', { feat : i for i, feat in enumerate(['time'] + IP_HEADER + TCP_HEADER) })

    def featurize(self, raw_pkt, timestamp=None):
        """
        Returns a list of basic features as defined by the BasicFeatures enum
        raw_pkt: The scapy Packet_metaclass instance to be converted
        timestamp: the artificial timestamp (useful for preexisting, converted packets)
        """

        features = [None for i in self.BasicFeatures]

        if timestamp:
            features[self.BasicFeatures['time'].value] = timestamp
        else:
            features[self.BasicFeatures['time'].value] = raw_pkt.time

        if IP in raw_pkt:
            for feat in IP_HEADER:
                features[self.BasicFeatures[feat].value] = getattr(raw_pkt[IP], feat)

        if TCP in raw_pkt:
            for feat in TCP_HEADER:
                features[self.BasicFeatures[feat].value] = getattr(raw_pkt[TCP], feat)

        return features


class BasicFeaturizerUDP(object):

    def __init__(self):

        self.BasicFeatures = self._feature_enum()

    def _feature_enum(self):
        """
        Returns an Enum mapping 'time' and all features in IP_HEADER and TCP_HEADER
        to a range of values beginning at 0
        """

        return Enum('Features', { feat : i for i, feat in enumerate(['time', 'is_tcp', 'is_ip'] + IP_HEADER + TCP_HEADER) })

    def featurize(self, raw_pkt, timestamp=None):
        """
        Returns a list of basic features as defined by the BasicFeatures enum
        raw_pkt: The scapy Packet_metaclass instance to be converted
        timestamp: the artificial timestamp (useful for preexisting, converted packets)
        """

        features = [None for i in self.BasicFeatures]

        if timestamp:
            features[self.BasicFeatures['time'].value] = timestamp
        else:
            features[self.BasicFeatures['time'].value] = raw_pkt.time

        features[self.BasicFeatures['is_tcp'].value] = 1 if TCP in raw_pkt else 0
        features[self.BasicFeatures['is_ip'].value] = 1 if IP in raw_pkt else 0



        for feat in IP_HEADER:
            if IP in raw_pkt:
                features[self.BasicFeatures[feat].value] = getattr(raw_pkt[IP], feat)
            else:
                features[self.BasicFeatures[feat].value] = 0    

        for feat in TCP_HEADER:
            if TCP in raw_pkt:
                features[self.BasicFeatures[feat].value] = getattr(raw_pkt[TCP], feat)
            elif UDP in raw_pkt and feat in UDP_HEADER:
                features[self.BasicFeatures[feat].value] = getattr(raw_pkt[UDP], feat)
            else:
                features[self.BasicFeatures[feat].value] = 0

        return features


class CountBasedFeaturizer(BasicFeaturizer):

    def __init__(self, pkt_window=50):

        self.pkt_window = pkt_window
        self.pkt_history = deque()

        self.BasicFeatures = super(type(self), self)._feature_enum()

        self.feature_stats = { feat : defaultdict(int) for feat in self.BasicFeatures }

    def _cull_history(self):
        """
        Removes old featurized packets from self.pkt_history
        Updates self.feature_stats
        """

        if len(self.pkt_history) > self.pkt_window:

            trash_pkt = self.pkt_history.popleft()

            for feat in self.BasicFeatures:

                self.feature_stats[feat][trash_pkt[feat.value]] -= 1

    def _increment_history(self, pkt):
        """
        Adds the featurized packet to the self.pkt_history
        Updates self.feature_stats
        """

        self.pkt_history.append(pkt)

        for feat in self.BasicFeatures:

            self.feature_stats[feat][pkt[feat.value]] += 1

    def _update_history(self, pkt):
        """
        Increments and culls packet history and feature stats
        """

        self._increment_history(pkt)
        self._cull_history()

    def featurize(self, raw_pkt):

        pkt = super(type(self), self).featurize(raw_pkt)

        self._update_history(pkt)

        pkt.extend([self.feature_stats[self.BasicFeatures(i)][pkt[i]] for i in range(len(pkt))])

        return pkt


class TimeBasedFeaturizer(BasicFeaturizer):

    def __init__(self, sec_window=10):

        self.sec_window = sec_window
        self.pkt_history = deque()

        self.BasicFeatures = super(type(self), self)._feature_enum()

        self.feature_stats = { feat : defaultdict(int) for feat in self.BasicFeatures }

    def _cull_history(self, pkt):
        """
        Removes old featurized packets from self.pkt_history
        Updates self.feature_stats
        """

        now = pkt[self.BasicFeatures.time.value]

        while now - self.pkt_history[0][self.BasicFeatures.time.value] > self.sec_window:

            trash_pkt = self.pkt_history.popleft()

            for feat in self.BasicFeatures:

                self.feature_stats[feat][trash_pkt[feat.value]] -= 1

    def _increment_history(self, pkt):
        """
        Adds the featurized packet to the self.pkt_history
        Updates self.feature_stats
        """

        self.pkt_history.append(pkt)

        for feat in self.BasicFeatures:

            self.feature_stats[feat][pkt[feat.value]] += 1

    def _update_history(self, pkt):
        """
        Increments and culls packet history and feature stats
        """

        self._increment_history(pkt)
        self._cull_history(pkt)

    def featurize(self, raw_pkt):

        pkt = super(type(self), self).featurize(raw_pkt)

        self._update_history(pkt)

        pkt.extend([self.feature_stats[self.BasicFeatures(i)][pkt[i]] for i in range(len(pkt))])

        return pkt

if __name__ == '__main__':
    reader = read_tcpdump_file('data/week1_friday.tcpdump')

    print('Test CountBasedFeaturizer')
    CBF = CountBasedFeaturizer(50)
    pkts_read = 0
    while True:
        pkt_read = reader.__next__()
        raw_pkt = Ether(pkt_read[1])
        if IP in raw_pkt and TCP in raw_pkt:
            feats = CBF.featurize(raw_pkt)
            pkts_read += 1
        if pkts_read > CBF.pkt_window * 2:
            break

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

    print("Test BasicFeaturizerUDP")
    BFU = BasicFeaturizerUDP()

    pkts_read = 0
    while True:
        pkt_read = reader.__next__()
        raw_pkt = Ether(pkt_read[1])
        cur_len = -1
        if IP in raw_pkt:
            feats = BFU.featurize(raw_pkt)
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
            feats = BFU.featurize(raw_pkt)
            assert(feats[2] == 0)
        pkts_read += 1 
        if pkts_read > 10000:
            break

