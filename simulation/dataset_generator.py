from test_data import Data_point, Test_data
from utils import *
from scapy.all import *

def generate_test_data(source='darpa', max_packets=200):
	if source == "darpa":
		dps = []

		reader = read_tcpdump_file('data/week2_thursday.tcpdump')
		filtered_pkts = filter_pkts(reader, max_packets=max_packets)
		dps.extend([Data_point(pkt, malicious=True) for pkt in filtered_pkts])

		reader = read_tcpdump_file('data/week1_thursday.tcpdump')
		filtered_pkts = filter_pkts(reader, max_packets=max_packets)
		dps.extend([Data_point(pkt, malicious=False) for pkt in filtered_pkts])

		return Test_data(dps)
	else:
		DUMMY_DATA_POINTS = [
		    Data_point(Ether(dst='88:88:88:88:88:88', src='66:66:66:66:66:66') / \
		        IP(dst='1.1.1.1', src='2.2.2.2', len=5, id=1, chksum=5) / TCP(chksum=5), malicious=True)
		]
		DUMMY_TEST_DATA = Test_data(DUMMY_DATA_POINTS)
		return DUMMY_TEST_DATA
