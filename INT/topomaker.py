import json
import random

def generate_topology(num_hosts, num_switches):
    data = {
        "hosts": {},
        "switches": {},
        "links": []
    }

    # Generate hosts
    for i in range(1, num_hosts + 1):
        host_name = f"h{i}"
        data["hosts"][host_name] = {
            "ip": f"fc00::{i}",
            "mac": f"08:00:00:00:{i:02d}:{i:02d}",
            "commands": [
                f"route add default gw fc00::{i*10:X} dev eth0",
                f"arp -i eth0 -s fc00::{i*10:X} 08:00:00:00:{i:02d}:00"
            ]
        }
    
    super_host_name = f"h{num_hosts+1}"
    data["hosts"][super_host_name] = {
            "ip": f"fc00::{num_hosts+1}",
            "mac": f"08:00:00:00:{num_hosts+1:02d}:{num_hosts+1:02d}",
            "commands": [
                f"route add default gw fc00::{(num_hosts+1)*10:X} dev eth0",
                f"arp -i eth0 -s fc00::{(num_hosts+1)*10:X} 08:00:00:00:{num_hosts+1:02d}:00"
            ]
        }
    
    # Generate switches
    for i in range(1, num_switches + 1):
        switch_name = f"s{i}"
        data["switches"][switch_name] = {
            "runtime_json": f"topo/{switch_name}-runtime.json"
        }

    # Track switch 
    num_core_switches = 6
    access_switchs = {f"s{i}": 1 for i in range(1, num_switches + 1 - num_core_switches)}
    core_switchs = {"s{}".format(i): 1 for i in range(num_switches + 1 - num_core_switches, num_switches + 1)}

    # Track nodes
    num_clients = num_hosts // 2
    num_compute_nodes = num_hosts - num_clients

    # 生成客户端和接入交换机之间的链接
    for i in range(1, num_clients + 1):
        host_name = f"h{i}"
        switch_name = f"s{i}"
        port = access_switchs[switch_name]
        data["links"].append([host_name, f"{switch_name}-p{port}"])
        access_switchs[switch_name] += 1

    # 生成算力节点和接入交换机之间的链接
    for i in range(num_clients + 1, num_hosts + 1):
        host_name = f"h{i}"
        switch_name = f"s{i}"
        port = access_switchs[switch_name]
        data["links"].append([host_name, f"{switch_name}-p{port}"])
        access_switchs[switch_name] += 1
    
    for i in range(1, num_switches + 1 - num_core_switches):
        host_name = super_host_name
        switch_name = f"s{i}"
        port = access_switchs[switch_name]
        data["links"].append([host_name, f"{switch_name}-p{port}"])
        access_switchs[switch_name] += 1

# 随机生成接入交换机和核心交换机之间的连接端口数量
    for i in range(1, num_switches + 1 - num_core_switches):
        switch_name = "s{}".format(i)
        num_ports = random.randint(1, num_core_switches)  # 每个接入交换机随机连接到1到num_core_switches个核心交换机
        
        for cs_index in range(1, num_core_switches+1):
            core_switch_name = "s{}".format(num_switches + 1 - cs_index)
            port1 = access_switchs[switch_name]
            port2 = core_switchs[core_switch_name]
            data["links"].append(["{}-p{}".format(switch_name, port1), "{}-p{}".format(core_switch_name, port2)])
            access_switchs[switch_name] += 1
            core_switchs[core_switch_name] += 1

    
    
    # # Generate links between switches in a linear topology
    # for i in range(1, num_switches):
    #     switch1 = f"s{i}"
    #     switch2 = f"s{i+1}"
    #     port1 = switchs[switch1]
    #     port2 = switchs[switch2]
    #     data["links"].append([f"{switch1}-p{port1}", f"{switch2}-p{port2}"])
    #     switchs[switch1] += 1
    #     switchs[switch2] += 1

    return data



def save_topology_to_json(topology, filename):
    with open(filename, 'w') as f:
        json.dump(topology, f, indent=4)

def generate_switch(num_switches):
    for i in range(1, num_switches + 1):
        switch_name = f"s{i}"
        filename = f"./topo/{switch_name}-runtime.json"
        switch_runtime = {
            "target": "bmv2",
            "p4info": "build/INT.p4.p4info.txt",
            "bmv2_json": "build/INT.json",
            "table_entries": [
            ]
        }
        with open(filename, 'w') as f:
            json.dump(switch_runtime, f, indent=4)

num_hosts = 12  # 可以根据需求修改
num_clients = num_hosts // 2
num_compute_nodes = num_hosts - num_clients
num_switches = 18  # 可以根据需求修改

if __name__ == '__main__':


    topology = generate_topology(num_hosts, num_switches)
    generate_switch(num_switches)
    save_topology_to_json(topology, './topo/topology.json')