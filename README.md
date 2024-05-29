# ServiveNAT
P4_16 based service address translation (including v1model architecture and TNA architecture).  
This is a P4 program that ensures L4 connectivity (such as TCP) while completing network address translation.  
It's called ***ServiceNAT*** because we use it for service address to host address translation, which is part of the base experiment our paper.  
Our experiment was conducted on physical devices and did not involve mininet code.  

## 1 ServiceNAT based on v1model architecture (IPv4)
### 1.1 Test Topology
                      | **Server** |——————————————|**Bmv2_Switch**|—————————————| **Client** |  
                      |172.18.100.2|              |  SW Bind port |             |172.18.101.2|
Note: The IP address is marked as the connection address of the physical interface.We assume that the service IP address is **128.0.0.1**. MAC address is based on actual. 

### 1.2 Operating sequence
(1) Compile P4, generate .json file: 
- `p4c --target bmv2 --arch v1model --std p4-16 ServiceNAT_v1model.p4`
    
(2) Activate simple_switch and bind port:
- `sudo simple_switch --device-id 152 -i 1@enp6s0f1 -i 2@enp5s0f0 -i 3@enp6s0f0 --thrift-port 9090 ServiceNAT_v1model.json`
- See simple_switch description for details.

(3) Flowtable:
- `simple_switch_CLI --thrift-port 9090 <ServiceNAT_simple-switch-flowtable_v1model.txt`

(4)Test by iperf:
- `iperf -s`
- `iperf -c 128.0.0.1`

Our re-calculation of the L4 checksum makes use of functions integrated with the v1model.  
If successful, the service address issued by the client is converted to the server's interface address. The client makes a normal TCP connection to the server and the iperf result is displayed on both sides.For the user, it establishes a connection to the _**service address**_. And for the server, it establishes a connection to the **_specific host address_**.  


## 2 ServiceNAT based on TNA architecture (IPv6)
### 2.1 Test Topology
                      |**Server**|———————————————|**Tofino_Switch**|——————————————|**Client**|  
                      |2000::250 |               |   Switch port   |              |2000::152 |
Note: The IP address is marked as the connection address of the physical interface.We assume that the service IP address is **2000::4**. MAC address is based on actual.

### 2.2 Operating sequence  

Our Tofino switch model is an Intel S9180 with sde9.7.0.
(1)Booting and connecting the switch： 
- sudo ssh root@_tofino console IP_

(2)Configuring the Tofino Switch:
- `cd bf-sde-9.7.0`Entering the SDE environment.
- `source set_sde.bash`Configure SDE environment variables such as **$SDE,$SDE_INSTALL**.
- `veth_setup.sh`loading port.
- `./install/bin/bf_kdrv_mod_load $SDE_INSTALL`Loading the kernel driver.

(3)Compiling P4 files:
- `scp packet_name -r root@tofino console IP:/bf-sde-9.7.0/pkgsrc/p4-examples/p4_16_programs/`Copy file to path.
- `cd /bf-sde-9.7.0/p4studio/`Go to the compile folder and use the cmake file inside to compile p4.
- `cmake -DCMAKE_INSTALL_PREFIX=$SDE/install -DCMAKE_MODULE_INSTALL_PATH=$SDE/cmake -DP4_NAME=file_name -DP4_PATH=/bf-sde-9.7.0/pkgsrc/p4-examples/p4_16_programs/file_name/file_name.p4`
- `make`
- `make install`Successful if no Error is prompted in the middle of the process.

(4)Run P4 project:
- `cd /bf-sde-9.7.0/`
- `./run_switch -p XX`If it runs successfully, it will go to the _bfshell>_ command line.

(5)Port Configuration:
- `ucli`Go to the user command line _bf-sde>_.
- `port-add 33/- 10G NONE`Port, Bandwidth, Negotiation.
- `port-enb 33/-`Enable port.
- `pm show`Enabling is successful if the opened port OPT shows **UP**.

(6)Flowtable:
- `exit`return _bfshell>_.
- `bfrt_python`
- `bfrt`
- `bfrt.tofino_p4nat.pipe.SwitchIngress.ipv6_c2s`Until find the table you want.
- `add_with_ipv6_c2s_forward()`The name of the action is different, so be careful, the name of the action here is _ipv6_c2s_forward_.
- The rules for add_with_table() are as follows:For example, if the `KEY` in the table is an `ipv6 address`, and the variables for the match action are the `MAC address`, and the `port number`:
  - `add_with_ipv6_c2s_forward(‘0x200000000000000000000000000000000004’, ‘00:16:fe:ec:4e:ab’ ,65)`
  - The flow table required for this experiment is detailed in **ServiceNAT_tofino-flowtable**.

(7)Terminal NDP issues:  
- Since there is no ICMP support involved, you need to configure the NDP protocol manually.
- `Ip -6 neigh`View Neighbourhood Relationships.
- `sudo ip -6 neigh add [IPv6] lladdr [MAC] dev [NIC name] nud permanent`

(8)Test by iperf:
- `iperf -s -V`
- `iperf -c 2000::4 -V`

Our recalculation of the L4 checksum uses the incremental calculation method of **RFC 1642**.  
If successful, the service address issued by the client is converted to the server's interface address. The client makes a normal TCP connection to the server and the iperf result is displayed on both sides.For the user, it establishes a connection to the _**service address**_. And for the server, it establishes a connection to the **_specific host address_**. 
