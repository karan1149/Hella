from time import sleep

import sys, os
sys.path.append(os.path.expandvars('../ml'))
sys.path.append(os.path.expandvars('../monitor'))
from monitor import Monitor
from method import Method
from generate import generate_test_data

class Simulator():
    def __init__(self):
        print("Gathering test data...")
        test_data = generate_test_data('darpa')
        self.monitor = Monitor(test_data, send_fn=self.send_to_method)
        self.method = Method(send_fn=self.send_to_monitor)

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
    simulator = Simulator()
    simulator.run()
