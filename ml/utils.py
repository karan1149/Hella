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

    yield packet

if __name__ == "__main__":
  packets = read_tcpdump_file("outside.tcpdump")
  featurizer = featurize_packets(packets)
  for f in featurizer:
    print(f)
