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

# Reads scapy pkts directly from a tcpdump file
def read_scapy_pkts(tcpdump_file, max_packets=float('inf')):
  reader = read_tcpdump_file(tcpdump_file)
  pkts_read = 0
  for raw_pkt in reader:
    scapy_pkt = Ether(raw_pkt[1])
    if IP in scapy_pkt and TCP in scapy_pkt:   
        pkts_read += 1
        yield scapy_pkt
    if pkts_read > max_packets: 
        break


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
  results = []
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
      continue

    try:
      tcp = ip.data
      for key in TCP_FEATURES:
        packet.append(tcp[key])
    except:
      continue
    results.append(packet)
    
  return results

def filter_pkts(pkts, max_packets=None):
  i = 0
  for ts, buf in pkts:
    if i == max_packets:
      return
    eth = dpkt.ethernet.Ethernet(buf)
    packet = [ts]

    try:
      ip = eth.data
      for key in IP_FEATURES:
        packet.append(ip[key])
    except:
      continue

    try:
      tcp = ip.data
      for key in TCP_FEATURES:
        packet.append(tcp[key])
    except:
      continue
    i += 1
    yield (ts, buf)

def featurize_dpkt_pkt(pkt):
  return featurize_packets([pkt])[0]

if __name__ == "__main__":
  packets = read_tcpdump_file("outside.tcpdump")
  featurizer = featurize_packets(packets)
  for f in featurizer:
    print(f)