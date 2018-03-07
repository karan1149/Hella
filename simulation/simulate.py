from time import sleep

import sys, os
sys.path.append(os.path.expandvars('../ml'))
sys.path.append(os.path.expandvars('../monitor'))
from monitor import Monitor
from method import Method

class Simulator():
    def __init__(self):
        self.monitor = Monitor(send_fn=self.send_to_method)
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
