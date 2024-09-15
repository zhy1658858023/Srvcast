#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IPv6, UDP, TCP

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print ("Cannot find eth0 interface")
        exit(1)
    return iface

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('ip_srcaddr', type=str, help="The destination IP address to use")
    parser.add_argument('ip_dstaddr', type=str)
    parser.add_argument('message', type=str, help="The message to include in packet")
    args = parser.parse_args()

    src_addr = args.ip_srcaddr
    dst_addr = args.ip_dstaddr
    iface = get_if()

    print ("sending on interface {}" .format(iface))
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt /IPv6(src=src_addr, dst=dst_addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / args.message
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
