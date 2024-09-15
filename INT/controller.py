import json
from collections import defaultdict
from topomaker import num_clients, num_compute_nodes, num_switches

# 读取JSON文件
def read_topology(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# 构建邻接表和端口映射
def build_graph(data):
    graph = defaultdict(list)
    port_mapping = {}
    for link in data["links"]:
        node1, node2 = link
        if '-' in node1:
            switch1, port1 = node1.split('-')
        else:
            switch1, port1 = node1, None
        
        if '-' in node2:
            switch2, port2 = node2.split('-')
        else:
            switch2, port2 = node2, None
        
        graph[switch1].append(switch2)
        graph[switch2].append(switch1)
        
        if port1:
            port_mapping[(switch1, switch2)] = int(port1[1:])
        if port2:
            port_mapping[(switch2, switch1)] = int(port2[1:])
    
    return graph, port_mapping

# 深度优先搜索生成路径
def dfs(graph, start, end, path=None):
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return path
    for node in graph[start]:
        if node not in path:
            new_path = dfs(graph, node, end, path)
            if new_path:
                return new_path
    return None

# 根据路径生成流表配置命令
def generate_flow_table(path, data, port_mapping):
    commands = []
    end_host = path[len(path) - 1]
    for i in range(len(path) - 1):
        current = path[i]
        next_node = path[i + 1]
        last_node = path[i-1]
        if current.startswith('s'):
            filename  = './flowtable/'+path[i] + '-commands.txt'
            with open(filename, 'a+') as file:
                if last_node.startswith('h'):
                    commands.append(f"table_add swtrace add_swtrace => {int(current.split('s')[1])}")
                    file.write(commands[-1]+'\n')
                else:
                    commands.append(f"table_add swtrace transition_swtrace => {int(current.split('s')[1])}")
                    file.write(commands[-1]+'\n')

                port = port_mapping[(current, next_node)]
                host_info = data['hosts'][end_host]
                ip = host_info['ip']
                mac = host_info['mac']
                commands.append(f"table_add ipv6_lpm ipv6_forward {ip} => {mac} {port}")
                file.write(commands[-1]+'\n')        
               
    return commands

def dis_flow_table(path):
    filename = "start.sh"
    with open(filename, 'w+') as file:
        file.write('#!/bin/bash\ncd ./flowtable\n')
        for i in range(len(path) - 1):
            current = path[i]
            if current.startswith('s'):
                file.write(f"simple_switch_CLI --thrift-port {9089 + int(current.split('s')[1])} < {current}-commands.txt\n")

def clear_table(switches):
    for i in range(1, switches+1):
        filename  = f"./flowtable/s{i}-commands.txt"
        with open(filename, 'w+') as file:
            pass
        

    

# 主函数
def main(json_file, start_host, end_host):
    # 读取拓扑
    data = read_topology(json_file)
    
    # 构建图和端口映射
    graph, port_mapping = build_graph(data)
    
    # 生成路径
    path = dfs(graph, start_host, end_host)
    
    # 生成流表配置命令
    if path:
        commands = generate_flow_table(path, data, port_mapping)
        print(path)
        for command in commands:
            print(command)
        dis_flow_table(path)
    else:
        print("No path found from {} to {}".format(start_host, end_host))

if __name__ == '__main__':
    clear_table(num_switches)
    # 示例JSON文件和起始/目标主机
    json_file = 'topo/topology.json'
    start_host = f"h{13}"
    end_host = f"h{10}"
    # 生成流表配置命令
    main(json_file, start_host, end_host)
    
    
    
