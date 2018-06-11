import argparse
from dataset import DataGenerator
import os
import random
import pickle
'''
Utility for creating datasets of a given size automatically by choosing asset files 
randomly.
By convention asset names ending in 0 are reserved for creating test datasets only!
'''
if __name__ == '__main__':

	parser = argparse.ArgumentParser()

	def check_positive(value):
	    ivalue = int(value)
	    if ivalue <= 0:
	         raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
	    return ivalue

	parser.add_argument('--num_packets', help='Number of packets to generate.', required=True, type=check_positive)
	parser.add_argument('--assets_path', help='The path to the folder containing asset files. Should just be "assets"', required=True)
	parser.add_argument('--data_file', help='The destination packet data path, ending in .pkl.', required=True)
	parser.add_argument('--test', help="Whether the dataset creation should involve asset files designated for test. Default false", action='store_true', default=False)

	args = parser.parse_args()

	asset_files = sorted(os.listdir(args.assets_path))
	if args.test:
		asset_files = [name for name in asset_files if name.endswith('0.csv')]
	else:
		asset_files = [name for name in asset_files if not name.endswith('0.csv')]
	assert(asset_files)
	packets = []
	files_used = []
	while len(packets) < args.num_packets:
		print("Currently have %d packets of %d..." % (len(packets), args.num_packets))
		if not asset_files:
			raise Exception("Ran out of asset files!")
		print("Choosing from %d asset files..." % len(asset_files))
		choice_index = random.randrange(0, len(asset_files))
		print("Chose %s" % asset_files[choice_index])
		files_used.append(asset_files[choice_index])
		path = os.path.join(args.assets_path, asset_files[choice_index])

		asset_files.pop(choice_index)
		
		data_generator = DataGenerator(path, 'temp_output')
		data_generator.build_dataset()

		with open('temp_output', 'rb') as f:
			packets.extend(pickle.load(f))

		os.remove('temp_output')

	print("Obtained %d packets, now cutting down to %d packets" % (len(packets), args.num_packets))
	packets = packets[:args.num_packets]
	with open(args.data_file, 'wb') as f:
		pickle.dump(packets, f)

	print("Done!")
	print("Files used:")
	print(files_used)



	# data_generator = DataGenerator(args.asset_file, args.data_file)
	# data_generator.build_dataset()