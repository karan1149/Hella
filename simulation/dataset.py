import json
import argparse
import csv
import datetime
import time as time_module
import collections
import pickle
import socket

from numpy import random, log
from tqdm import tqdm
from collections import defaultdict

import api

class DataGenerator():

	def __init__(self, asset_file, data_file):
		self.asset_file = asset_file
		self.data_file = data_file

		raw_asset = self.read_asset_file(self.asset_file)
		self.data_points = self.process_asset(raw_asset)
		self.config = self.read_config_file()

		self.api = api.API()

	def read_asset_file(self, in_file):
		"""
		parse asset from asset file
		return raw parse of asset
		"""
		asset = []
		with open(in_file, 'r') as asset_file:
			reader = csv.DictReader(asset_file)
			for row in reader:
				asset.append([float(row[key]) for key in ['TIME', 'LATITUDE','LONGITUDE']])
		return asset

	def process_asset(self, asset):
		"""
		add seconds granularity to asset
		add interpolated data points to asset
		return new asset
		"""
		asset = self.granular_asset(asset)
		asset = self.interpolated_asset(asset)
		return asset

	def granular_asset(self, asset):
		"""
		add seconds granularity to asset
		return granular asset
		"""
		granular_asset = []
		time_buckets = collections.defaultdict(list)

		for time, lat, lon in asset:
			time_buckets[time].append((time, lat, lon))

		for time_key in sorted(time_buckets.keys()):
			per_minute = len(time_buckets[time_key])
			seconds_per = 60 // per_minute

			for dp_i, data_point in enumerate(time_buckets[time_key]):
				time, lat, lon = data_point
				granular_asset.append((time + dp_i * seconds_per, lat, lon))

		return granular_asset	

	def interpolated_asset(self, asset):
		"""
		add interpolated data points to asset
		return interpolated asset
		"""
		interpolated_asset = []

		for dp_i in range(len(asset) - 1):
			curr_dp = asset[dp_i]
			next_dp = asset[dp_i + 1]

			between_asset = []
			start_time, start_lat, start_lon = curr_dp
			end_time, end_lat, end_lon = next_dp

			seconds_delta = int(end_time - start_time)
			lat_delta = end_lat - start_lat
			lon_delta = end_lon - start_lon

			time_increment = 1
			lat_increment = lat_delta / seconds_delta
			lon_increment = lon_delta / seconds_delta

			for s_i in range(seconds_delta):
				between_time = start_time + s_i * time_increment
				between_lat = start_lat + s_i * lat_increment
				between_lon = start_lon + s_i * lon_increment
				between_asset.append((between_time, between_lat, between_lon))

			interpolated_asset.extend(between_asset)

		return interpolated_asset

	def read_config_file(self, in_file='dataset_gen_config.json'):
		"""
		read in the probabilistic configuration parameters
		return the config dictionary 
		"""
		with open(in_file, 'r') as jsonfile:
			config = json.load(jsonfile)
		return config

	def build_dataset(self):

		init_datetime = datetime.datetime.fromtimestamp(self.data_points[0][0])
		seconds_passed = init_datetime.minute * 60 + init_datetime.second

		all_packets = []
		request_counts = defaultdict(int)

		for time, lat, lon in tqdm(self.data_points):
			now_datetime = datetime.datetime.fromtimestamp(time)

			is_weekday = now_datetime.weekday() < 5
			is_weekend = not is_weekday
			is_dawn = now_datetime.hour >= 0 and now_datetime.hour < 6
			is_morning = now_datetime.hour >= 6 and now_datetime.hour < 12
			is_afternoon = now_datetime.hour >= 12 and now_datetime.hour < 18
			is_evening = now_datetime.hour >= 18 and now_datetime.hour < 24

			do_elevation = seconds_passed % self.config['elevation']['frequency'] == 0 and \
						   random.binomial(1, self.config['elevation']['prob']) == 1

			do_places 	 = seconds_passed % self.config['places_nearby']['frequency'] == 0 and \
						   (
							   (random.binomial(1, self.config['places_nearby']['prob_night']) == 1 and (is_dawn or is_evening)) or
							   (random.binomial(1, self.config['places_nearby']['prob_day']) == 1 and (is_morning or is_afternoon))
						   )

			do_location	 = seconds_passed % self.config['location_info']['frequency'] == 0 and \
						   random.binomial(1, self.config['location_info']['prob']) == 1


			do_weather	 = seconds_passed % self.config['weather']['frequency'] == 0 and \
						   random.binomial(1, self.config['weather']['prob']) == 1


			do_news		 = seconds_passed % self.config['news']['frequency'] == 0 and \
						   (
							   (random.binomial(1, self.config['news']['prob_weekday_morning']) == 1 and is_morning and is_weekday) or
							   (random.binomial(1, self.config['news']['prob_weekday_day']) == 1 and (is_afternoon or is_weekday)) or
							   (random.binomial(1, self.config['news']['prob_weekend_morning']) == 1 and is_morning and is_weekend) or
							   (random.binomial(1, self.config['news']['prob_weekend_day']) == 1 and (is_afternoon or is_weekend))
						   )

			do_update 	 = seconds_passed % self.config['update']['frequency'] == 0 and \
						   random.binomial(1, self.config['update']['prob']) == 1

			do_check_updates 	 = seconds_passed % self.config['check_updates']['frequency'] == 0 and \
						   		   random.binomial(1, self.config['check_updates']['prob']) == 1

			try:
				if do_elevation:
					self.api.perform_get(api.GET_LOCATION_ELEVATION_FN(lat, lon))
				if do_places: 
					self.api.perform_get(api.GET_LOCATION_NEARBY_FN(lat, lon))
				if do_location: 
					self.api.perform_get(api.GET_LOCATION_INFO_FN(lat, lon))
				if do_weather: 
					self.api.perform_get(api.GET_LOCATION_WEATHER_FN(lat, lon))
				if do_news: 
					self.api.perform_get(api.GET_NEWS_HEADLINES_FN)
				if do_update:
					self.api.perform_get(api.GET_LATEST_UPDATE)
				if do_check_updates:
					self.api.perform_get(api.GET_UPDATE_INFO)
			except socket.timeout:
				print("Exception: socket timed out. skipping request batch.")
				continue

			request_counts['elevation'] += int(do_elevation)
			request_counts['places_nearby'] += int(do_places)
			request_counts['location_info'] += int(do_location)
			request_counts['weather'] += int(do_weather)
			request_counts['news'] += int(do_news)
			request_counts['update'] += int(do_update)
			request_counts['check_updates'] += int(do_check_updates)

			raw_packets = self.api.drain_pkts()
			self.transfer_timestamps(time, raw_packets)
			all_packets.extend(raw_packets)

			seconds_passed += 1
			time_module.sleep(0.05)
		
		self.dataset = all_packets
		self.save_dataset(all_packets, request_counts)

		return all_packets

	def transfer_timestamps(self, real_time, packets):
		if len(packets) == 0: return
		start_time = packets[0].time
		for packet in packets:
			time_delta = packet.time - start_time
			packet.time = real_time + time_delta		

	def save_dataset(self, raw_packets, request_counts):
		pickle.dump(raw_packets, open(self.data_file, 'wb'))
		print('REQUEST COUNT STATISTICS')
		for key in request_counts:
			print('{}: {}'.format(key, request_counts[key]))


if __name__ == '__main__':

	parser = argparse.ArgumentParser()

	parser.add_argument('--asset_file', help='The file path for the desired asset file.', required=True)
	parser.add_argument('--data_file', help='The destination packet data path, ending in .pkl.', required=True)

	args = parser.parse_args()
	
	data_generator = DataGenerator(args.asset_file, args.data_file)
	data_generator.build_dataset()