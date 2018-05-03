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
    def __init__(self, model_file, data_file, is_training, verbosity):
        self.model_file = model_file
        self.data_file = data_file
        self.is_training = is_training

        self.monitor = Monitor(None, log_level=verbosity, send_fn=self.send_to_method)
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
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='more log verbosity')

    parser.add_argument('model_file')

    parser.add_argument('--data_file', default=None, help='dataset source file')

    train_test = parser.add_mutually_exclusive_group(required=True)
    train_test.add_argument('--train', action='store_true', help='train the model')
    train_test.add_argument('--test', action='store_true', help='test the model')

    args = parser.parse_args()

    simulator = Simulator(args.model_file, args.data_file, args.train, int(args.verbose))
    simulator.run()