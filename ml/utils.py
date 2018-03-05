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

def featurize_packets(packets):
  """
  """
  for ts, buf in packets:
    eth = dpkt.ethernet.Ethernet(buf)

    packets = [ts]

    try:
      ip = eth.data
      for key in IP_FEATURES:
        packets.append(ip[key])
    except:
      print("Exception in IP parse")
      continue

    try:
      tcp = ip.data      
      for key in TCP_FEATURES:
        packets.append(tcp[key])
    except:
      print("Exception in TCP parse")
      continue

    yield packets

if __name__ == "__main__":
  packets = read_tcpdump_file("outside.tcpdump")
  featurizer = featurize_packets(packets)
  for f in featurizer:
    print(f)