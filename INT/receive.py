#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys
import json



from scapy.all import IPv6, TCP, get_if_list, sniff, UDP
from int_header import *
HOPS = 13
ShimSize = 4
INTSize = 12
MetadataSize = 25
int_data = {
    
}


def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def handle_pkt(pkt):
    if int_shim_header in pkt :
        print("got a packet")
        # pkt.show()
#        hexdump(pkt)
#        print "len(pkt) = ", len(pkt)
        p1 = pkt.copy()
        print(1)
        p1 = p1.payload.payload.payload

        p1_bytes = bytes(p1)

        int_shim_header(p1_bytes[0:ShimSize]).show()
        p1_bytes = p1_bytes[ShimSize:]

        int_header(p1_bytes[0:INTSize]).show()
        p1_bytes = p1_bytes[INTSize:]

        for i in range(HOPS):
            p2 = int_metadata(p1_bytes[0:MetadataSize])
            extract_int_info(p2)
            p2.show()
            p1_bytes = p1_bytes[MetadataSize:]
        sys.stdout.flush()

def extract_int_info(packet):
    int_metadata_layer = packet[int_metadata]
    switch_id = int_metadata_layer.switchID
    hop_delay = int_metadata_layer.hop_delay
    queue_depth = int_metadata_layer.queue_depth
    queue_delay = int_metadata_layer.queue_delay

    int_data["swid"+str(switch_id)] = {
        "hop_delay": str(hop_delay)+"us",
        "queue_depth": str(queue_depth) + "pkt",
        "queue_delay": str(queue_delay) + "us"
    }
    filename = "int_data.json"
    with open(filename, 'w') as f:
        json.dump(int_data, f, indent=4)



def main():
    ifaces = [i for i in os.listdir('/sys/class/net/') if 'eth' in i]
    iface = get_if()
    print("sniffing on %s" % iface)
    sys.stdout.flush()
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
