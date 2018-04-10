from time import sleep

import sys, os
sys.path.append(os.path.expandvars('../ml'))
sys.path.append(os.path.expandvars('../monitor'))
from monitor import Monitor
from method import Method
import dataset_generator
import api
import argparse

class Simulator():
    def __init__(self, verbosity, dataset_filename):
        print('Gathering test data...')
        test_data = self.generate_test_data(True, dataset_filename)
        self.monitor = Monitor(test_data, send_fn=self.send_to_method, log_level=int(args.verbosity))
        self.method = Method(send_fn=self.send_to_monitor)

    # note that in order to use the api, you must run with sudo
    # in order to send and receive real packets with scapy
    def generate_test_data(self, use_api, dataset_filename):
        return api.generate_test_data(dataset_filename) if use_api \
            else dataset_generator.generate_test_data('darpa')

    def send_to_method(self, pkt):
        self.method.handle_pkt(pkt)

    def send_to_monitor(self, pkt):
        self.monitor.handle_pkt(pkt)

    def run(self):
        self.monitor.send()
        while not self.monitor.completed():
            sleep(.1)
        self.monitor.show_results()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbosity') # 0 or 1
    parser.add_argument('--dataset',
        help='specify a filename for the generated pcap file', type=str)
    args = parser.parse_args()
    if args.verbosity is None:
        args.verbosity = 0

    simulator = Simulator(args.verbosity, args.dataset)
    simulator.run()
