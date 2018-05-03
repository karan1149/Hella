from time import sleep

import sys, os
sys.path.append(os.path.expandvars('../ml'))
sys.path.append(os.path.expandvars('../monitor'))
from monitor import Monitor
from method import Method
import api
import argparse

class Simulator():

    def __init__(self, model_file, data_file, is_training, verbosity):
        """
        This class will eventually simulate real communication between 
        the api, method, and monitor. This behavior only makes sense for
        when the system is "deployed" aka making requests in real time.

        Currently, it serves to stitch together the method and monitor 
        (train/test and display) of static data.
        """        
        self.model_file = model_file
        self.data_file = data_file
        self.is_training = is_training
        self.verbosity = verbosity

        # requires sudo to send and receive real packets
        self.api = api.API()

    def train(self):
        """
        Train the model on data in data_file and save to model_file
        model_file: pkl file to write to
        data_file:  pcap file to read from
        """
        self.method = Method(api=self.api, send_fn=self.send_to_monitor)
        self.method.train_model(self.model_file, self.data_file)

    def test(self):
        """
        Test the model loaded from model_file on data in data_file
        model_file: pkl file to read from
        data_file:  pcap file to read from
        verbosity:  verbosity
        """
        self.method = Method(api=self.api, send_fn=self.send_to_monitor)   
        self.method.load_model(self.model_file)

        self.monitor = Monitor(log_level=self.verbosity, send_fn=self.send_to_method)
        self.monitor.load_data(self.data_file)

        self.monitor.send()
        while not self.monitor.completed():
            sleep(.1)
        self.monitor.show_results() 

    def run(self):
        """
        Run the simulation in train or test mode
        """
        if self.is_training:
            self.train()
        else:
            self.test()

    def send_to_method(self, pkt):
        self.method.handle_pkt(pkt)

    def send_to_monitor(self, pkt):
        self.monitor.handle_pkt(pkt)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='the log verbosity')

    parser.add_argument('data_file', help='the .pkl file to read packets from (--train) or Test_data from (--test)')
    parser.add_argument('model_file', help='the .pkl file to write to (--train) and read from (--test)')

    train_test = parser.add_mutually_exclusive_group(required=True)
    train_test.add_argument('--train', action='store_true', help='train the model')
    train_test.add_argument('--test', action='store_true', help='test the model')

    args = parser.parse_args()

    simulator = Simulator(args.model_file, args.data_file, args.train, int(args.verbose))
    simulator.run()