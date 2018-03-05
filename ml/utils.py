import dpkt

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
    ip = eth.data
    tcp = ip.data
    # if len(tcp.data) > 0 and tcp.dport == 80:
    #   http = dpkt.http.Request(tcp.data)
    # else:
    #   http = b''
    yield ts, eth, ip, tcp
