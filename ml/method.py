from scapy.all import *

from headers import Seer
from anomaly_model import AnomalyModel
from utils import *
from api import GET_UPDATE, GET_UPDATE_INFO, GET_LATEST_UPDATE

ETH_BROADCAST = 'ff:ff:ff:ff:ff:ff'

# TODO: update with actual ethernet address of ECU
ETH_SRC = ETH_BROADCAST

class Method():
    def __init__(self, api, send_fn=sendp):
        self.model = AnomalyModel()
        self.load_model()
        self.api = api
        self.send_fn = send_fn

    def load_model(self):
        try:
            self.model.load('model.pkl')
        except:
            packets = []

            reader = read_tcpdump_file('data/week1_monday.tcpdump')
            packets.extend(featurize_packets(reader))

            reader = read_tcpdump_file('data/week1_tuesday.tcpdump')
            packets.extend(featurize_packets(reader))

            reader = read_tcpdump_file('data/week1_wednesday.tcpdump')
            packets.extend(featurize_packets(reader))

            reader = read_tcpdump_file('data/week1_friday.tcpdump')
            packets.extend(featurize_packets(reader))

            print("Fitting on %d packets" % len(packets))

            self.model.fit(packets)
            self.model.save('model.pkl')

    def make_requests(self):
        for r in [GET_UPDATE_INFO, GET_LATEST_UPDATE, GET_UPDATE]:
            self.api.perform_get(r)

    def handle_pkt(self, pkt):
        featurize_fn = featurize_scapy_pkt if 'scapy' in str(type(pkt)) \
            else featurize_dpkt_pkt
        featurized_pkt = featurize_fn(pkt)
        prediction = self.model.predict(featurized_pkt)
        ether = Ether(dst=ETH_BROADCAST, src=ETH_SRC)
        seer = Seer(malicious=prediction, data=pkt)
        self.send_fn(ether / seer)

    def run(self):
        sniff(prn=self.handle_pkt, count=0)
