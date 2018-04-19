from collections import deque, defaultdict
from enum import Enum, unique

import time

# IP_FEATURES = ['len', 'id', 'off', 'ttl', 'p', 'sum']
# TCP_FEATURES = ['sport', 'dport', 'seq', 'ack', 'flags', 'win', 'sum']

class BasicFeaturizer:

	def __init__(self):
		pass

	def featurize_basic(self, pkt):
		"""
		Converts a scapy packet into a list of features.
		"""
		features = [pkt.time]
		if IP in pkt:
		features.extend([pkt[IP].len, pkt[IP].id, pkt[IP].frag, \
			pkt[IP].ttl, pkt[IP].proto, pkt[IP].chksum])
		if TCP in pkt:
		features.extend([pkt[TCP].sport, pkt[TCP].dport, pkt[TCP].seq, \
			pkt[TCP].ack, pkt[TCP].flags, pkt[TCP].window, pkt[TCP].chksum])
		return features

class TimeBasedFeaturizer():

	def __init__(self, window=50):

		self.window = window
		self.pkt_history = deque()

		self.features = Enum('Features', ['time'] + IP_FEATURES + TCP_FEATURES)

		self.ip_feature_stats = { key : defaultdict(int) for ip_feature in IP_FEATURES }
		self.tcp_feature_stats = { key : defaultdict(int) for tcp_feature in TCP_FEATURES }

	def cull_history(self, now):

		while now - self.pkt_history[0][0] > self.window * 1000:

			trash_pkt = self.pkt_history.popleft()

			self.ip_feature_stats[trash_pkt]

	def increment_history(self, pkt):

		self.pkt_history.append(pkt)

	def featurize(self, pkt):
		pass

