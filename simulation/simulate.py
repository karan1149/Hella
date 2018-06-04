from time import sleep

import sys, os
sys.path.append(os.path.expandvars('../ml'))
sys.path.append(os.path.expandvars('../monitor'))
from monitor import Monitor
from method import Method
from featurizer import BasicFeaturizer, CountBasedFeaturizer, TimeBasedFeaturizer, BasicFeaturizerUDP
import api
import argparse
from scapy.all import *
import pickle
import time

featurizer_classes = { 1: BasicFeaturizer, 2: CountBasedFeaturizer, 3: TimeBasedFeaturizer, 4: BasicFeaturizerUDP}

class Simulator():

    def __init__(self, model_file, data_file, out_file, attack_type,
        is_training, verbosity, featurizer=None):
        """
        This class will eventually simulate real communication between
        the api, method, and monitor. This behavior only makes sense for
        when the system is "deployed" aka making requests in real time.

        Currently, it serves to stitch together the method and monitor
        (train/test and display) of static data.
        """
        self.model_file = model_file
        self.data_file = data_file
        self.out_file = out_file
        self.attack_type = attack_type
        self.is_training = is_training
        self.verbosity = verbosity
        self.featurizer = featurizer

        # requires sudo to send and receive real packets
        self.api = api.API()

    def train(self):
        """
        Train the model on data in data_file and save to model_file
        model_file: pkl file to write to
        data_file:  pcap file to read from
        """
        self.method = Method(api=self.api, send_fn=self.send_to_monitor)
        self.method.train_model(self.model_file, self.data_file, self.featurizer)

    def test(self):
        """
        Test the model loaded from model_file on data in data_file
        model_file: pkl file to read from
        data_file:  pcap file to read from
        verbosity:  verbosity
        """
        self.method = Method(api=self.api, send_fn=self.send_to_monitor)
        self.method.load_model(self.model_file)

        self.monitor = Monitor(log_level=self.verbosity, send_fn=self.send_to_method,
            attack_type=self.attack_type)
        pkts = []
        with open(self.data_file, 'rb') as f:
            pkts = pickle.load(f)
        self.monitor.create_test_data(pkts)

        self.monitor.send()
        start_time = time.time()
        # time out after 10 seconds
        while not self.monitor.completed() and time.time() - start_time < 10:
            sleep(.1)
        self.monitor.show_results()

        if self.out_file:
            pickle.dump(self.monitor.test_data, open(self.out_file, 'wb'))

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
