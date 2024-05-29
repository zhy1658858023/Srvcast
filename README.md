# ServiveNAT
P4_16 based service address translation (including v1model architecture and TNA architecture).  
This is a P4 program that ensures L4 connectivity (such as TCP) while completing network address translation.  
It's called ***ServiceNAT*** because we use it for service address to host address translation, which is part of the base experiment our paper.  
Our experiment was conducted on physical devices and did not involve mininet code.  

## 1 ServiceNAT based on v1model architecture (IPv4)
### 1.1 Test Topology
                      |**Server**|———————————————|**Bmv2_Switch**|——————————————|**Client**|  
Interface ip address  172.18.100.2            simple-switch bind port            172.18.101.2             
### 1.2 Operating sequence


## 2 ServiceNAT based on TNA architecture (IPv6)
### 2.1 Test Topology

### 1.2 Operating sequence
