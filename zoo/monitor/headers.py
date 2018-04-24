from scapy.all import *

# This is an unused ethernet type
ETHERTYPE_SEER = 0x0100

class Seer(Packet):
    name = 'seer'
    fields_desc = [
        ByteField('malicious', 0),
        # hold length of data, autocalculated on build
        FieldLenField('data_len', None, length_of='data'),
        # the original packet should follow the Seer header
        StrLenField('data', '', length_from=lambda x: x.data_len),
    ]

# Seer packets should be broadcast out of all Ethernet ports to reach the monitor
# For now, it is assumed that the monitor is a direct neighbor of the ECU
# If that changes, we can have Seer run over IP instead of over Ethernet,
# using the IP address of the monitor
bind_layers(Ether, Seer, type=ETHERTYPE_SEER)
