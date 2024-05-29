# ServiveNAT
P4_16 based service address translation (including v1model architecture and TNA architecture).  
This is a P4 program that ensures L4 connectivity (such as TCP) while completing network address translation.  
It's called ***ServiceNAT*** because we use it for service address to host address translation, which is part of the base experiment our paper.  
Our experiment was conducted on physical devices and did not involve mininet code.  

## 1 ServiceNAT based on v1model architecture (IPv4)
### 1.1 Test Topology
                      |**Server**|———————————————|**Bmv2_Switch**|——————————————|**Client**|  
                      |172.18.100.2|             |  SW Bind port |              |172.18.101.2|
Note: The IP address is marked as the connection address of the physical interface.  

### 1.2 Operating sequence
(1) Compile P4, generate .json file  
>`p4c --target bmv2 --arch v1model --std p4-16 xxx.p`    
(2) Activate simple_switch  
>`sudo simple_switch --device-id 152 -i 1@enp6s0f1 -i 2@enp5s0f0 -i 3@enp6s0f0 --thrift-port 9090 xx.json`  
## 2 ServiceNAT based on TNA architecture (IPv6)
### 2.1 Test Topology

### 1.2 Operating sequence
