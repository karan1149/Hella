# based off of https://stackoverflow.com/questions/37683026/how-to-create-http-get-request-scapy/37716000

from scapy.all import *
from threading import Thread

sys.path.append(os.path.expandvars('../monitor'))
from test_data import Data_point, Test_data

GET_BASE = 'GET {} HTTP/1.1\r\nHost: seer-autohub.herokuapp.com\r\n\r\n'
API_DST = 'seer-autohub.herokuapp.com'
API_BASE = '/api/v1/'
API_KEY = '0279615b-5cb4-4070-abd9-4b9909aca6af'
GET_UPDATE_INFO = API_BASE + 'car/updates/list?key=%s' % API_KEY
GET_LATEST_UPDATE = API_BASE + 'car/updates/latest?key=%s' % API_KEY
GET_UPDATE_FUNC = lambda id_: API_BASE + 'car/update?id=%s&key=%s' % (id_, API_KEY)
UPDATE_ID = '7d93e61d-2dd2-4829-ac94-4a6c5edc52d3'
GET_UPDATE = GET_UPDATE_FUNC(UPDATE_ID)

TCP_FIN = 0x01
HTTP_PORT = 80

class API():
    def __init__(self):
        self.recv_pkts = []

        socket.setdefaulttimeout(5)
        self.api_ip = socket.gethostbyname(API_DST)

    def drain_pkts(self):
        pkts = self.recv_pkts
        self.recv_pkts = []
        return pkts

    def perform_get(self, query):
        print('Performing GET...')

        # sniff traffic from the get on a thread
        capture_thread = Thread(target=self.capture_pkts)
        # daemon threads don't prevent program from exiting
        capture_thread.setDaemon(True)
        capture_thread.start()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((self.api_ip, HTTP_PORT))

        get = GET_BASE.format(query)
        sock.sendall(bytes(get, 'utf-8'))
        # block until packets are received
        data = self.recvall(sock)

        # send fin flag to close TCP connection
        # and indicate to capture thread to stop
        sock.shutdown(1)

        capture_thread.join(timeout=1)

        sock.close()

    # from https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data?lq=1
    def recvall(self, sock):
        BUFF_SIZE = 4096 # 4 KiB
        data = b''
        while True:
            part = sock.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                # either 0 or end of data
                break
        return data

    # TODO: do we want to capture egress traffic as well?
    def capture_pkts(self):
        # sniff until we see a fin flag
        pkts = sniff(filter='src host {}'.format(self.api_ip), count=0,
            stop_filter=lambda p: p[TCP].flags & TCP_FIN == TCP_FIN)
        self.recv_pkts.extend(pkts)

def generate_test_data():
    api = API()
    api.perform_get(GET_UPDATE_INFO)
    api.perform_get(GET_LATEST_UPDATE)
    api.perform_get(GET_UPDATE)
    pkts = api.drain_pkts()
    return Test_data([Data_point(p, malicious=False) for p in pkts])

# to test that the script runs properly
if __name__ == '__main__':
    generate_test_data()
