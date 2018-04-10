from scapy.all import *

from headers import Seer
from anomaly_model import AnomalyModel
from utils import *
from collections import deque
import pickle

ETH_BROADCAST = 'ff:ff:ff:ff:ff:ff'
WINDOW_SIZE = 20

# TODO: update with actual ethernet address of ECU
ETH_SRC = ETH_BROADCAST

class Method():
    def __init__(self, send_fn=sendp):
        self.model = AnomalyModel()
        self.load_model()
        self.send_fn = send_fn
        self.packet_queue = deque()

    def load_model(self):
        try:
            self.model.load('model.pkl')
        except:
            with open('features.pkl', 'w') as f:
                try: 
                    featurized_pkts = pickle.load(f)
                except Exception as e:
                    print(e)
                    packets = []

                    reader = read_tcpdump_file('data/week1_monday.tcpdump')
                    packets.extend(filter_pkts(reader))

                    reader = read_tcpdump_file('data/week1_tuesday.tcpdump')
                    packets.extend(filter_pkts(reader))

                    reader = read_tcpdump_file('data/week1_wednesday.tcpdump')
                    packets.extend(filter_pkts(reader))

                    reader = read_tcpdump_file('data/week1_friday.tcpdump')
                    packets.extend(filter_pkts(reader))

                    featurized_pkts = []
                    queue = deque()
                    for packet in packets:
                        featurized_pkt = featurize_dpkt_pkt(packet, queue)
                        queue.append(featurized_pkt)
                        # Max len is WINDOW_SIZE - 1
                        if len(queue) > WINDOW_SIZE:
                            queue.popleft()
                        featurized_pkts.append(featurized_pkt)
                    pickle.dump(featurized_pkts, f)
                    print("Saved packets to file features.pkl")

                print("Fitting on %d packets" % len(featurized_pkts))
                print("Packet dim is %d" % len(featurized_pkts[0]))

                self.model.fit(featurized_pkts)
                self.model.save('model.pkl')

    def handle_pkt(self, pkt):
        featurized_pkt = featurize_dpkt_pkt(pkt, self.packet_queue)
        self.packet_queue.append(featurized_pkt)
        # Max len is WINDOW_SIZE - 1
        if len(self.packet_queue) > WINDOW_SIZE:
            self.packet_queue.popleft()
        prediction = self.model.predict(featurized_pkt)
        ether = Ether(dst=ETH_BROADCAST, src=ETH_SRC)
        seer = Seer(malicious=prediction, data=pkt)
        self.send_fn(ether / seer)

    def run(self):
        sniff(prn=self.handle_pkt, count=0)
