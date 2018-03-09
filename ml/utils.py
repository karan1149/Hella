from scapy.all import *
import dpkt

IP_FEATURES = ['len', 'id', 'off', 'ttl', 'p', 'sum']
TCP_FEATURES = ['sport', 'dport', 'seq', 'ack', 'flags', 'win', 'sum']

def read_tcpdump_file(tcpdump_file):
  """
  Reads the tcpdump file and returns a list of packets (bytes).
  """
  with open(tcpdump_file, 'rb') as f:
    pcap = dpkt.pcap.Reader(f)
    for ts, buf in pcap:
      yield ts, buf

def featurize_scapy_pkt(pkt):
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

def featurize_packets(packets):
  """
  """
  for ts, buf in packets:
    eth = dpkt.ethernet.Ethernet(buf)
    # Note: if you want to convert packets to scapy packets,
    # you can do pkt = Ether(buf)

    packet = [ts]

    try:
      ip = eth.data
      for key in IP_FEATURES:
        packet.append(ip[key])
    except:
      print("Exception in IP parse")
      continue

    try:
      tcp = ip.data
      for key in TCP_FEATURES:
        packet.append(tcp[key])
    except:
      print("Exception in TCP parse")
      continue

    yield packet

if __name__ == "__main__":
  packets = read_tcpdump_file("outside.tcpdump")
  featurizer = featurize_packets(packets)
  for f in featurizer:
    print(f)