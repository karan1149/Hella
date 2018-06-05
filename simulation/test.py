import argparse
from simulate import Simulator

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='the log verbosity')

    parser.add_argument('-d', '--data_file', help='the .pkl file to read Test_data from')
    parser.add_argument('-m', '--model_file', help='the .pkl (saved model) file to read from')
    parser.add_argument('-o', '--out_file', help='the .pkl file to save the test data to')
    parser.add_argument('-a', '--attack_type',
        help='the type of attack to incorporate into the simulation', default=None)

    args = parser.parse_args()

    simulator = Simulator(args.model_file, args.data_file, args.out_file,
        args.attack_type, False, int(args.verbose))
    simulator.run()
