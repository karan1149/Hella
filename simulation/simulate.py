from time import sleep

import sys, os
sys.path.append(os.path.expandvars('../ml'))
sys.path.append(os.path.expandvars('../monitor'))
from monitor import Monitor
from method import Method
import dataset_generator
import api
import argparse

DATASET_EXT = '.pcap'

class Simulator():
    # note that in order to use the api, you must run with sudo
    # in order to send and receive real packets with scapy
    def __init__(self, verbosity, use_api, dataset_filename):
        self.api = api.API() if use_api else None
        self.dataset_filename = dataset_filename
        self.monitor = Monitor(None, send_fn=self.send_to_method, log_level=int(args.verbosity))
        self.method = Method(self.api, send_fn=self.send_to_monitor)

    def generate_test_data(self):
        return dataset_generator.generate_test_data('darpa')

    def send_to_method(self, pkt):
        self.method.handle_pkt(pkt)

    def send_to_monitor(self, pkt):
        self.monitor.handle_pkt(pkt)

    def run(self):
        self.create_test_data()

        self.monitor.send()
        while not self.monitor.completed():
            sleep(.1)
        self.monitor.show_results()

        self.save_to_file()

    def create_test_data(self):
        print('Gathering test data...')
        if self.api:
            self.method.make_requests()
            pkts = self.api.drain_pkts()
            self.monitor.create_test_data(pkts, should_fuzz=True)
        else:
            test_data = self.generate_test_data()
            self.monitor.set_test_data(test_data)

    # saves the packets used for the simulation to a file if desired
    def save_to_file(self):
        if not self.dataset_filename: return

        if not self.dataset_filename.endswith(DATASET_EXT):
            self.dataset_filename = ''.join([dataset_filename, DATASET_EXT])
        wrpcap(self.dataset_filename, pkts)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbosity') # 0 or 1
    parser.add_argument('--api', action='store_true', default=False)
    parser.add_argument('--dataset',
        help='specify a filename for the generated pcap file', type=str)
    args = parser.parse_args()
    if args.verbosity is None:
        args.verbosity = 0

    simulator = Simulator(args.verbosity, args.api, args.dataset)
    simulator.run()
