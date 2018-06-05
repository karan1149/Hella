from scapy.all import *
from threading import Thread
from collections import namedtuple
import random

from headers import Seer
from test_data import Data_point, Test_data

FUZZ_THRESHOLD = .3 # fuzz 30% of packets
NUM_SYNS = 100 # send 100 syn packets per src IP for syn flooding
ATTACKER_ETHER = 'd4:d5:d6:d7:d7:d9' # for arp spoof attack

FUZZ_ATTACK_TYPE = 'fuzz'
SYN_FLOOD_ATTACK_TYPE = 'syn-flood'
TEARDROP_ATTACK_TYPE = 'teardrop'
DNS_ATTACK_TYPE = 'dns'
ATTACK_TYPES = [FUZZ_ATTACK_TYPE, SYN_FLOOD_ATTACK_TYPE, \
    TEARDROP_ATTACK_TYPE]

LOG_LEVEL_MINIMAL = 0
LOG_LEVEL_VERBOSE = 1

LOG_LEVEL_DEFAULT = LOG_LEVEL_MINIMAL

to_pred = lambda prediction: 'MALICIOUS' if prediction else 'BENIGN'
to_rate = lambda num, denom: 'None' if not denom else '{}%'.format(round((num/float(denom)) * 100, 2))


class Monitor():
    def __init__(self, log_level=LOG_LEVEL_DEFAULT, send_fn=sendp, attack_type=None):
        self.log_level = log_level
        self.send_fn = send_fn
        self.attack_type = attack_type

        # shouldn't need a lock for the test data because the same values are
        # not accessed from different threads
        self.listen_thread = Thread(target=
            lambda: sniff(filter='seer', prn=self.handle_pkt, count=0))
        # daemon threads don't prevent program from exiting
        self.listen_thread.setDaemon(True)

    def set_test_data(self, test_data):
        self.test_data = test_data

    def create_test_data(self, pkts):
        data_points = []
        if not self.attack_type:
            data_points.extend([Data_point(p, malicious=False) for p in pkts])
        else:
            if self.attack_type == FUZZ_ATTACK_TYPE:
                for p in pkts:
                    if random.random() < FUZZ_THRESHOLD:
                        data_points.append(Data_point(fuzz(p), malicious=True))
                    else:
                        data_points.append(Data_point(p, malicious=False))
            elif self.attack_type == SYN_FLOOD_ATTACK_TYPE:
                for p in pkts:
                    syn_flood_pkt = p.copy()
                    syn_flood_pkt[IP].remove_payload()
                    syn_flood_pkt = syn_flood_pkt / TCP(flags='S') / ('X'*10)
                    data_points.extend([Data_point(syn_flood_pkt,
                        malicious=True) for i in range(NUM_SYNS)])
                    data_points.append(Data_point(p, malicious=False))
            elif self.attack_type == TEARDROP_ATTACK_TYPE:
                # inspired by: https://github.com/unregistered436/scapy/blob/master/teardrop.py
                # perform teardrop attack from src IP of pkt 0
                ether = pkts[0][Ether].copy()
                ether.remove_payload()
                ip = pkts[0][IP].copy()
                ip.remove_payload()

                # TODO: this should be UDP and not TCP once
                # UDP featurization works
                p = ether / ip.copy() / TCP() / ('X'*10)
                p[IP].id = 42
                p[IP].flags = 'MF'
                data_points.append(Data_point(p, malicious=True))

                p = ether / ip.copy() / TCP() / ('X'*116)
                p[IP].id = 42
                p[IP].frag = 48
                data_points.append(Data_point(p, malicious=True))

                p = ether / ip.copy() / TCP() / ('X'*224)
                p[IP].id = 42
                p[IP].flags = 'MF'
                data_points.append(Data_point(p, malicious=True))

                data_points.extend([Data_point(p, malicious=False) for p in pkts])
            else:
                raise Exception('Unsupported attack type')

        self.test_data = Test_data(data_points)

    def send(self):
        if LOG_LEVEL_VERBOSE == self.log_level:
            print('##############################################')
            print('STARTING...')
        for dp in self.test_data.dps:
            if LOG_LEVEL_VERBOSE == self.log_level:
                print('SENT: Test packet to Method with value: {}'.format(to_pred(dp.malicious)))
            self.send_fn(dp.pkt)

    def handle_pkt(self, pkt):
        prediction = pkt[Seer].malicious
        dp = self.test_data.dp_for_pkt(pkt[Seer].data)

        if LOG_LEVEL_VERBOSE == self.log_level:
            print('RECEIVED: Prediction packet from Method with value: {}'.format(to_pred(prediction)))

        if dp:
            dp.prediction = prediction

    # Listen for seer packets sent from the intrusion detection system to the
    # monitor to indicate whether a specific packet was classified as malicious
    def listen(self):
        self.listen_thread.start()

    def completed(self):
        return len(self.test_data.completed_dps()) == len(self.test_data.dps)

    def show_results(self):
        if not self.completed():
            print('WARNING: not all packets predicted')

        total_sent = len(self.test_data.dps)
        total_classified = len(self.test_data.completed_dps())
        total_correct = len(self.test_data.correct_dps())
        num_malicious = len(list(filter(lambda dp: dp in self.test_data.completed_dps(),
            self.test_data.malicious_dps())))
        num_benign = len(list(filter(lambda dp: dp in self.test_data.completed_dps(),
            self.test_data.benign_dps())))
        num_false_pos = len(self.test_data.false_positive_dps())
        num_false_neg = len(self.test_data.false_negative_dps())

        print('##############################################')
        print('RESULTS:')
        print('--------')
        print('Total packets sent: {}'.format(total_sent))
        print('Total packets classified: {}'.format(total_classified))
        print('Total correctly classified: {}'.format(total_correct))
        print('Percent correctly classified: {}'.format(to_rate(total_correct, total_classified)))
        print('False negative rate: {}'.format(to_rate(num_false_neg, num_malicious)))
        print('False positive rate: {}'.format(to_rate(num_false_pos, num_benign)))
        print('##############################################')

    def run(self):
        self.send()
        self.listen()


if __name__ == '__main__':
    monitor = Monitor()
    monitor.run()
