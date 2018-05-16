from os import path
import pickle
import sys

from scapy.all import *

from featurizer import *
from headers import Seer
from anomaly_model import AnomalyModel
from utils import *
from api import GET_UPDATE, GET_UPDATE_INFO, GET_LATEST_UPDATE

ETH_BROADCAST = 'ff:ff:ff:ff:ff:ff'

# TODO: update with actual ethernet address of ECU
ETH_SRC = ETH_BROADCAST

class Method():
    def __init__(self, api=None, send_fn=sendp):
        self.api = api
        self.send_fn = send_fn

        self.model = AnomalyModel()

    def load_model(self, model_file):
        try:
            self.model.load(model_file)
        except:
            print("Unable to load %s. Abort.)" % (model_file))
            exit(0)

    def train_model(self, model_file, data_file, featurizer=BasicFeaturizer):
        fr = featurizer()
        raw_pkts = pickle.load(open(data_file, 'rb'))
        pkts = [fr.featurize(raw_pkt) for raw_pkt in raw_pkts]
        self.model.featurizer = fr.__class__.__name__

        print("Fitting on %d packets" % len(pkts))

        self.model.fit(pkts)
        self.model.save(model_file)

    def make_requests(self):
        for r in [GET_UPDATE_INFO, GET_LATEST_UPDATE, GET_UPDATE]:
            self.api.perform_get(r)

    def handle_pkt(self, pkt):
        fr = getattr(sys.modules[__name__], self.model.featurizer)()

        featurized_pkt = fr.featurize(pkt)
        prediction = self.model.predict(featurized_pkt)
        ether = Ether(dst=ETH_BROADCAST, src=ETH_SRC)
        seer = Seer(malicious=prediction, data=pkt)
        self.send_fn(ether / seer)

    def run(self):
        sniff(prn=self.handle_pkt, count=0)