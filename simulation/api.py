# based off of https://stackoverflow.com/questions/37683026/how-to-create-http-get-request-scapy/37716000

from scapy.all import *
from test_data import Data_point, Test_data

API_DST = 'seer-autohub.herokuapp.com'
API_BASE = '/api/v1/'
API_KEY = '0279615b-5cb4-4070-abd9-4b9909aca6af'
GET_UPDATE_INFO = API_BASE + 'car/updates/list?key=%s' % API_KEY
GET_LATEST_UPDATE = API_BASE + 'car/updates/latest?key=%s' % API_KEY
GET_UPDATE_FUNC = lambda id_: API_BASE + 'car/update?id=%s&key=%s' % (id_, API_KEY)
UPDATE_ID = '7d93e61d-2dd2-4829-ac94-4a6c5edc52d3'
GET_UPDATE = GET_UPDATE_FUNC(UPDATE_ID)

FIN = 0x01
SCAPY_PORT = 9999
HTTP_PORT = 80
STARTING_SEQNO = 42

DATASET_EXT = '.pcap'

"""
Note:
The kernal will not recognize the source port as open, so it will
respond to the API's SYNACK with a reset packet, which will mess
up the connection. In order to get the kernal to ignore packets destined
to a certain port, run the following command (it is recommended that you
do this from a virtual machine instead of modifying your own kernal):
iptables -t raw -A PREROUTING -p tcp --dport <source port I use for scapy traffic> -j DROP
"""
class API():
    def __init__(self):
        self.recv_pkts = []

    def perform_get(self, query):
        print('Performing GET...')

        get = 'GET {} HTTP/1.1\r\nHost: seer-autohub.herokuapp.com\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nConnection: keep-alive\r\n\r\n'.format(query)

        # Send syn and receive synack
        syn_pkt = IP(dst=API_DST) / TCP(sport=SCAPY_PORT, dport=80, flags='S', seq=STARTING_SEQNO)
        synack_pkt = sr1(syn_pkt, timeout=2)
        if not synack_pkt: return
        self.recv_pkts.append(synack_pkt)

        # Create ack with get request
        ack_pkt = IP(dst=synack_pkt[IP].src) / TCP(sport=synack_pkt.dport,
            dport=HTTP_PORT, flags='A', seq=synack_pkt.ack, ack=synack_pkt.seq + 1) / get

        while True:
            reply_pkt = sr1(ack_pkt, timeout=2)
            if not reply_pkt: break
            self.recv_pkts.append(reply_pkt)

            # TODO: update with a full TCP sequence looking for FIN flag
            contains_response = 'HTTP/1.1' in reply_pkt[TCP].payload
            if (reply_pkt[TCP].flags & FIN) == FIN or contains_response: break

            data_len = reply_pkt[IP].len - len(IP()) - len(TCP())
            ackno = reply_pkt[TCP].seq + data_len
            # original ack packet may have 0 data
            flags = 'A' if data_len > 0 or ack_pkt[TCP].payload == get else 'AF'

            ack_pkt = IP(dst=reply_pkt[IP].src) / TCP(sport=reply_pkt[TCP].dport,
                dport=HTTP_PORT, flags=flags, seq=reply_pkt[TCP].ack, ack=ackno)

def generate_test_data(dataset_filename):
    api = API()
    api.perform_get(GET_UPDATE_INFO)
    api.perform_get(GET_LATEST_UPDATE)
    api.perform_get(GET_UPDATE)
    if (dataset_filename):
        if not dataset_filename.endswith(DATASET_EXT):
            dataset_filename = ''.join([dataset_filename, DATASET_EXT])
        wrpcap(dataset_filename, api.recv_pkts)
    return Test_data([Data_point(p, malicious=False) for p in api.recv_pkts])
