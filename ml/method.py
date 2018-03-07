from scapy.all import *

from headers import Seer
from anomaly_model import AnomalyModel

ETH_BROADCAST = 'ff:ff:ff:ff:ff:ff'

# TODO: update with actual ethernet address of ECU
ETH_SRC = ETH_BROADCAST

class Method():
    def __init__(self, send_fn=sendp):
        self.model = AnomalyModel()
        self.send_fn = send_fn

    def handle_pkt(self, pkt):
        prediction = self.model.predict(pkt)
        ether = Ether(dst=ETH_BROADCAST, src=ETH_SRC)
        seer = Seer(malicious=prediction, data=pkt)
        self.send_fn(ether / seer)

    def run(self):
        sniff(prn=self.handle_pkt, count=0)
