from scapy.all import *
from threading import Thread
from collections import namedtuple
import random

from headers import Seer
from test_data import Data_point, Test_data

FUZZ_THRESHOLD = .3 # fuzz 30% of packets

LOG_LEVEL_MINIMAL = 0
LOG_LEVEL_VERBOSE = 1

LOG_LEVEL_DEFAULT = LOG_LEVEL_MINIMAL

to_pred = lambda prediction: 'MALICIOUS' if prediction else 'BENIGN'
to_rate = lambda num, denom: 'None' if not denom else '{}%'.format(round((num/float(denom)) * 100, 2))


class Monitor():
    def __init__(self, test_data, log_level=LOG_LEVEL_DEFAULT, send_fn=sendp):
        self.test_data = test_data
        self.log_level = log_level
        self.send_fn = send_fn

        # shouldn't need a lock for the test data because the same values are
        # not accessed from different threads
        self.listen_thread = Thread(target=
            lambda: sniff(filter='seer', prn=self.handle_pkt, count=0))
        # daemon threads don't prevent program from exiting
        self.listen_thread.setDaemon(True)

    def set_test_data(self, test_data):
        self.test_data = test_data

    def create_test_data(self, pkts, should_fuzz):
        if not should_fuzz:
            self.test_data = Test_data([Data_point(p, malicious=False) for p in pkts])
        else:
            data_points = []
            for i in range(len(pkts)):
                if random.random() < FUZZ_THRESHOLD:
                    data_points.append(Data_point(fuzz(pkts[i]), malicious=True))
                else:
                    data_points.append(Data_point(pkts[i], malicious=False))
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
        assert self.completed()

        total_sent = len(self.test_data.dps)
        total_correct = len(self.test_data.correct_dps())
        num_malicious = len(self.test_data.malicious_dps())
        num_benign = len(self.test_data.benign_dps())
        num_false_pos = len(self.test_data.false_positive_dps())
        num_false_neg = len(self.test_data.false_negative_dps())

        print('##############################################')
        print('RESULTS:')
        print('--------')
        print('Total packets sent: {}'.format(total_sent))
        print('Total correctly classified: {}'.format(total_correct))
        print('Percent correctly classified: {}'.format(to_rate(total_correct, total_sent)))
        print('False negative rate: {}'.format(to_rate(num_false_neg, num_malicious)))
        print('False positive rate: {}'.format(to_rate(num_false_pos, num_benign)))
        print('##############################################')

    def run(self):
        self.send()
        self.listen()


if __name__ == '__main__':
    monitor = Monitor()
    monitor.run()
