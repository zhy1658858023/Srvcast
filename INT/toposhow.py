import json
import networkx as nx
import matplotlib.pyplot as plt

# 读取JSON文件
def read_topology(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# 创建网络拓扑图
def create_topology(data):
    G = nx.Graph()
    
    # 添加主机节点
    for host, attrs in data["hosts"].items():
        G.add_node(host, ip=attrs["ip"], mac=attrs["mac"], type='host')
    
    # 添加交换机节点
    for switch, attrs in data["switches"].items():
        G.add_node(switch, runtime_json=attrs["runtime_json"], type='switch')
    
    # 添加连接
    for link in data["links"]:
        node1, node2 = link[0], link[1]
        if '-' in node1:
            node1 = node1.split('-')[0]
        if '-' in node2:
            node2 = node2.split('-')[0]
        G.add_edge(node1, node2)
    
    return G

# 可视化拓扑图
def draw_topology(G):
    pos = nx.spring_layout(G)  # 使用spring layout布局
    
    # 提取主机和交换机节点
    host_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type' ) == 'host']
    switch_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type' ) == 'switch']
    
    # 绘制节点
    nx.draw_networkx_nodes(G, pos, nodelist=host_nodes, node_color='blue', node_shape='o', node_size=200, label='Hosts')
    nx.draw_networkx_nodes(G, pos, nodelist=switch_nodes, node_color='red', node_shape='s', node_size=200, label='Switches')
    
    # 绘制边
    nx.draw_networkx_edges(G, pos)
    
    # 绘制节点标签
    nx.draw_networkx_labels(G, pos)
    
    plt.legend(scatterpoints=1)
    plt.title('Network Topology')
    plt.savefig("topo")  # 保存为 PNG 文件
    plt.show()

if __name__ == '__main__':
    # 读取JSON文件内容
    filename = './topo/topology.json'
    data = read_topology(filename)
    
    # 创建拓扑图
    G = create_topology(data)
    
    # 可视化拓扑图
    draw_topology(G)
