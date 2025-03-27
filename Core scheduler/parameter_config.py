
def build_rtt_matrix():
    RTT = [[0 for _ in range(10)] for _ in range(10)]
    beijing = range(0, 4)
    chengwu = range(4, 8)
    guangzhou = range(8, 10)

    for group in [beijing, chengwu, guangzhou]:
        for i in group:
            for j in group:
                RTT[i][j] = 5

    for i in beijing:
        for j in guangzhou:
            RTT[i][j] = RTT[j][i] = 44

    for i in beijing:
        for j in chengwu:
            RTT[i][j] = RTT[j][i] = 33

    for i in chengwu:
        for j in guangzhou:
            RTT[i][j] = RTT[j][i] = 28

    return RTT

def build_Bw_matrix():
    Bw = [[0 for _ in range(10)] for _ in range(10)]
    beijing = range(0, 4)
    chengwu = range(4, 8)
    guangzhou = range(8, 10)

    for group in [beijing, chengwu, guangzhou]:
        for i in group:
            for j in group:
                Bw[i][j] = 20000

    for i in beijing:
        for j in guangzhou:
            Bw[i][j] = Bw[j][i] = 10000

    for i in beijing:
        for j in chengwu:
            Bw[i][j] = Bw[j][i] = 10000

    for i in chengwu:
        for j in guangzhou:
            Bw[i][j] = Bw[j][i] = 10000

    return Bw

def build_computation_cost():
    # 初始化11个元素，下标从1开始用
    k = [0] * 10

    # 北京：dc1-dc4，成本0.035
    for i in range(0, 4):
        k[i] = 0.035

    # 成都：dc5-dc8，成本0.025
    for i in range(4, 8):
        k[i] = 0.025

    # 广州：dc9-dc10，成本0.05
    for i in range(8, 10):
        k[i] = 0.05

    return k

def build_transmission_cost():
    T = [[0 for _ in range(10)] for _ in range(10)]
    beijing = range(0, 4)
    chengwu = range(4, 8)
    guangzhou = range(8, 10)

    # 城内传输成本 0.0025
    for group in [beijing, chengwu, guangzhou]:
        for i in group:
            for j in group:
                T[i][j] = 0.0025

    # 城间传输成本 0.004
    groups = [beijing, chengwu, guangzhou]
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            for a in groups[i]:
                for b in groups[j]:
                    T[a][b] = T[b][a] = 0.004
    return T

def build_dc_resources():
    compute_power = [0] * 10   # 下标1~10有效，单位：TFLOPs
    memory_capacity = [0] * 10 # 单位：GB

    for i in range(0, 10):
        compute_power[i] = 24540
        memory_capacity[i] = 10240

    return compute_power, memory_capacity
