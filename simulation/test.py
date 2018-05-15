import argparse
from simulate import Simulator
from scapy.all import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='the log verbosity')

    parser.add_argument('data_file', help='the .pkl file to read Test_data from')
    parser.add_argument('model_file', help='the .pkl (saved model) file to read from')

    args = parser.parse_args()

    simulator = Simulator(args.model_file, args.data_file, False, int(args.verbose))
    simulator.run()
