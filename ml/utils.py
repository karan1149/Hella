from scapy.all import *
import dpkt


def read_tcpdump_file(tcpdump_file):
  """
  Reads the tcpdump file and returns a list of packets (bytes).
  """
  with open(tcpdump_file, 'rb') as f:
    pcap = dpkt.pcap.Reader(f)
    for ts, buf in pcap:
      yield ts, buf

# Reads scapy pkts directly from a tcpdump file
def read_scapy_pkts(tcpdump_file, max_packets=float('inf'), allow_udp=False):
  reader = read_tcpdump_file(tcpdump_file)
  pkts_read = 0
  for raw_pkt in reader:
    scapy_pkt = Ether(raw_pkt[1])
    if allow_udp or (IP in scapy_pkt and TCP in scapy_pkt):   
        pkts_read += 1
        yield scapy_pkt
    if pkts_read > max_packets: 
        break