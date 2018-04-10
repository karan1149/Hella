from scapy.all import *
import dpkt
import method
import math

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
  results = []
  for ts, buf in packets:
    eth = dpkt.ethernet.Ethernet(buf)
    # Note: if you want to convert packets to scapy packets,
    # you can do pkt = Ether(buf)

    packet = [ts]

    ip = eth.data
    for key in IP_FEATURES:
      # print('ip', key, ip[key])
      packet.append(ip[key])

    tcp = ip.data
    for key in TCP_FEATURES:
      packet.append(tcp[key])
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

def featurize_dpkt_pkt(pkt, packet_queue):
  # First get individual features
  features = featurize_packets([pkt])[0]
  n_features = len(features)
  seen = len(packet_queue)
  for i in range(1, n_features):
    if i == 9 or i == 10:
      continue
    if seen == 0:
      features.append(features[i])
      features.append(0)
    else:
      total = 0.0
      totalSquared = 0.0
      for seen_pkt_features in packet_queue:
        total += seen_pkt_features[i]
        totalSquared += seen_pkt_features[i]**2
      mean = total / seen
      expectedSquared = totalSquared / seen
      stdev = math.sqrt(expectedSquared - mean**2)
      features.append(mean)
      features.append(stdev)

  curr_ts = features[0]
  time_differences = []
  for seen_pkt_features in packet_queue:
    then_ts = seen_pkt_features[0]
    time_differences.append(curr_ts - then_ts)

  if len(time_differences):
    time_mean = float(sum(time_differences)) / len(time_differences)
    time_stdev = math.sqrt(sum([(time - time_mean)**2 for time in time_differences]) / len(time_differences))
  else:
    time_mean = 0
    time_stdev = 0

  features.append(time_mean)
  features.append(time_stdev)

  return features

if __name__ == "__main__":
  packets = read_tcpdump_file("outside.tcpdump")
  featurizer = featurize_packets(packets)
  for f in featurizer:
    print(f)
