import sys, os
sys.path.append(os.path.expandvars('../ml'))
from featurizer import BasicFeaturizer, CountBasedFeaturizer, TimeBasedFeaturizer, BasicFeaturizerUDP
import argparse
from simulate import Simulator

featurizer_classes = { 1: BasicFeaturizer, 2: CountBasedFeaturizer, 3: TimeBasedFeaturizer, 4: BasicFeaturizerUDP}
# automatically generated help string for argparse
featurizer_help_string = ' | '.join([str(i) for i in sorted(featurizer_classes.keys())])

# https://mail.python.org/pipermail/tutor/2013-January/093635.html
def featurizer_range(arg):
    try:
        value = int(arg)
    except ValueError as err:
       raise argparse.ArgumentTypeError(str(err))

    if value < 1 or value > 4:
        message = "Expected 1 <= value <= 4, got value = {}".format(value)
        raise argparse.ArgumentTypeError(message)

    return value

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='the log verbosity')

    parser.add_argument('--data_file', help='The source .pkl file to read packets from. Should be a .pkl of a list of scapy packets.', required=True)
    parser.add_argument('--model_file', help='The destination .pkl file to write the model file to.', required=True)

    parser.add_argument('--featurizer', default=1, type=featurizer_range, help=featurizer_help_string)

    args = parser.parse_args()

    simulator = Simulator(args.model_file, args.data_file, True, int(args.verbose), featurizer=featurizer_classes[args.featurizer])
    simulator.run()
