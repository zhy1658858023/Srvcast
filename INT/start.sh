#!/bin/bash
cd ./flowtable
simple_switch_CLI --thrift-port 9090 < s1-commands.txt
simple_switch_CLI --thrift-port 9107 < s18-commands.txt
simple_switch_CLI --thrift-port 9091 < s2-commands.txt
simple_switch_CLI --thrift-port 9106 < s17-commands.txt
simple_switch_CLI --thrift-port 9092 < s3-commands.txt
simple_switch_CLI --thrift-port 9105 < s16-commands.txt
simple_switch_CLI --thrift-port 9093 < s4-commands.txt
simple_switch_CLI --thrift-port 9104 < s15-commands.txt
simple_switch_CLI --thrift-port 9094 < s5-commands.txt
simple_switch_CLI --thrift-port 9103 < s14-commands.txt
simple_switch_CLI --thrift-port 9095 < s6-commands.txt
simple_switch_CLI --thrift-port 9102 < s13-commands.txt
simple_switch_CLI --thrift-port 9099 < s10-commands.txt
