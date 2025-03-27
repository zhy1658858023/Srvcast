import os
import numpy as np
from copy import deepcopy
from itertools import combinations_with_replacement
from scipy.optimize import dual_annealing
from catch import find_best_fast
from parameter_config import build_rtt_matrix
from parameter_config import build_Bw_matrix
from parameter_config import build_computation_cost
from parameter_config import build_transmission_cost
from parameter_config import build_dc_resources



# 定义测试服务数据结构
class Service:
    def __init__(self, name, M, C, max_delay, max_cost, memory):
        self.name = name            # 服务名称
        self.M = M                  # 传输需求（Mbps等）
        self.C = C                  # 计算需求（比如CPU周期）
        self.max_delay = max_delay  # 最大时延（ms）
        self.max_cost = max_cost    # 最大成本（可自定义单位）
        self.memory = memory        # 所需内存（GB）

    def __repr__(self):
        return (f"Service({self.name}, M={self.M}, C={self.C}, delay≤{self.max_delay}, "
                f"cost≤{self.max_cost}, mem={self.memory}GB)")


# 定义策略n和v
def initialize_decision_variables():
    # n: 整数矩阵，初始化为0
    n = [[0 for _ in range(10)] for _ in range(10)]  # 任务卸载数量

    # v: 浮点数矩阵，初始化为0.0
    v = [[0.0 for _ in range(10)] for _ in range(10)]  # 资源分配量

    return n, v


# 时间计算函数
def processing_times(n, v, M, C, RTT, compute_power, B):
    processing_times = [[0.0 for _ in range(10)] for _ in range(10)]

    for i in range(0,10):
        for j in range(0,10):
            if n[i][j] > 0:
                # 传输时间：任务量 * M / 带宽 + RTT（注意RTT单位需转为秒）
                T_trans = ((n[i][j] * M) / B[i][j]) + (RTT[i][j] / 1000)  # ms -> s

                # 计算时间：任务量 * C / (能力 * 分配比例)
                if v[i][j] > 0:
                    T_comp = (n[i][j] * C) / (compute_power[j] * v[i][j])
                

                processing_times[i][j] = T_trans + T_comp
            else:
                processing_times[i][j] = 0.0

    return processing_times


# 成本计算函数
def compute_processing_cost(n, h, B, RTT, k, M, C):
    processing_cost = [[0.0 for _ in range(10)] for _ in range(10)]

    for i in range(10):
        for j in range(10):
            if n[i][j] > 0:
                # 传输成本项
                rtt_sec = RTT[i][j] / 1000  # ms → s
                trans_cost = (h[i][j] * M) + (h[i][j] * B[i][j] * rtt_sec) / n[i][j]

                # 计算成本项
                comp_cost = k[j] * C

                processing_cost[i][j] = trans_cost + comp_cost
            else:
                processing_cost[i][j] = 0.0

    return processing_cost


#计算处理时间和处理成本的加权效益
def P_score(n, T_total, processing_cost, w_time=0.7, w_cost=0.3):
    score = [[0.0 for _ in range(10)] for _ in range(10)]

    for i in range(10):
        for j in range(10):
            if n[i][j] > 0:
                score[i][j] = w_time * T_total[i][j] + w_cost * processing_cost[i][j]
            else:
                score[i][j] = 0.0  # 没有任务传输，无得分

    return score

def get_total_score_for_i(i, n, v, M, C, RTT, compute_power, B, h, k, w_time=0.7, w_cost=0.3):
    proc_time = processing_times(n, v, svc1.M, svc1.C, RTT, compute_power, Bw)
    proc_cost = compute_processing_cost(n, h, Bw, RTT, k, svc1.M, svc1.C)
    unit_score = P_score(n, proc_time, proc_cost, 0.7, 0.3)
    total = 0
    for j in range(10):
       total += n[i][j] * unit_score[i][j]
    return total


# 更新计算资源分配比例
def update_v_from_n(n):
    v = [[0.0 for _ in range(10)] for _ in range(10)]
    for j in range(0, 10):  # 被分配资源的数据中心
        total_tasks = sum(n[i][j] for i in range(0, 10))
        if total_tasks > 0:
            for i in range(0, 10):
                v[i][j] = n[i][j] / total_tasks
        elif total_tasks == 0:
                v[j][j] = 1
    return v


# # 遍历所有时间和成本(辅助函数)
# def print_all_processing_results(n, proc_time, proc_cost, P_score):
#     print("\n=== 所有非零任务的传输时间 / 计算时间 / 处理成本 ===")
#     for i in range(0, 10):
#         for j in range(0, 10):
#             if n[i][j] > 0:
#                 print(f"dc{i+1} → dc{j+1}:")
#                 print(f"  处理时间：{proc_time[i][j]:.4f} 秒")
#                 print(f"  处理成本：{proc_cost[i][j]:.4f} 元\n")
#                 print(f"  加权效益：{P_score[i][j]:.4f} 元\n")

def generate_task_allocations(N_i, num_dcs=10):
    # """生成所有长度为 num_dcs，元素和为 N_i 的非负整数组合"""
    if N_i == 0:
        yield [0] * num_dcs
        return

    def helper(n, k, prefix=[]):
        if k == 1:
            yield prefix + [n]
        else:
            for i in range(n + 1):
                yield from helper(n - i, k - 1, prefix + [i])

    yield from helper(N_i, num_dcs)


#核心函数，找最优组合的
def find_best(i, n, M, C, RTT, compute_power, B, h, k, w_time=0.7, w_cost=0.3):

    N_i = sum(n[i])
    if N_i == 0:
        return n[i]  # 无任务无需更新

    current_n_i = n[i][:]
    # print("初始组合：", n[i])
    v = update_v_from_n(n)
    current_score = get_total_score_for_i(i, n, v, M, C, RTT, compute_power, B, h, k, w_time, w_cost)
    # print(f"组合的得分为：{current_score:.4f}")
    best_score = current_score
    best_alloc = current_n_i[:]

    for alloc in generate_task_allocations(N_i):
        # print("生成组合：", alloc)
        if all(alloc[j] == current_n_i[j] for j in range(10)):
            continue  # 当前组合，跳过

        n_temp = deepcopy(n)
        n_temp[i] = alloc
        v_temp = update_v_from_n(n_temp)

        score = get_total_score_for_i(i, n_temp, v_temp, M, C, RTT, compute_power, B, h, k, w_time, w_cost)
        # print(f"组合的得分为：{score:.4f}")
        if score < best_score:
            best_score = score
            best_alloc = n_temp[i]
        else:
            continue
    return best_alloc



def find_best_fast(i, n, M, C, RTT, compute_power, B, h, k, w_time=0.7, w_cost=0.3, max_try=100, max_delay=8, max_cost=12):
    N_i = sum(n[i])
    if N_i == 0:
        return n[i]

    current_n_i = n[i][:]
    v_full = update_v_from_n(n)
    current_score = get_total_score_for_i(i, n, v_full, M, C, RTT, compute_power, B, h, k, w_time, w_cost)

    best_score = current_score
    best_alloc = current_n_i[:]
    has_feasible = False

    # ✅ Step 1: 仅尝试前 max_try 个组合
    for idx, alloc in enumerate(generate_task_allocations(N_i)):
        if idx >= max_try:
            break
        if alloc == current_n_i:
            continue

        n_temp = deepcopy(n)
        n_temp[i] = alloc
        v_temp = update_v_from_n(n_temp)

        T_total = processing_times(n_temp, v_temp, M, C, RTT, compute_power, B)
        proc_cost = compute_processing_cost(n_temp, h, B, RTT, k, M, C)

        # ✅ 判断每个任务是否满足单位时间/成本约束
        time_violation = any(
            T_total[i][j] > max_delay for j in range(10) if n_temp[i][j] > 0
        )
        cost_violation = any(
            proc_cost[i][j] > max_cost for j in range(10) if n_temp[i][j] > 0
        )

        if time_violation or cost_violation:
            continue  # 不满足任意一项约束，跳过

        has_feasible = True

        score = get_total_score_for_i(i, n_temp, v_temp, M, C, RTT, compute_power, B, h, k, w_time, w_cost)

        if score < best_score:
            best_score = score
            best_alloc = alloc[:]
        
    if not has_feasible:
        print(f"❌ dc{i} 无法找到满足 svc 约束的任务分配（任务数 {N_i}）")
        print(f"⚠️ 建议：提升目标数据中心的资源/带宽")
        return n[i]
    
    # ✅ Step 2: 从 best_alloc 开始进行贪心优化
    improved = True
    while improved:
        improved = False
        for j1 in range(10):
            if best_alloc[j1] == 0:
                continue
            for j2 in range(10):
                if j1 == j2:
                    continue
                temp = best_alloc[:]
                temp[j1] -= 1
                temp[j2] += 1
                n_temp = deepcopy(n)
                n_temp[i] = temp
                v_temp = update_v_from_n(n_temp)

                T_total = processing_times(n_temp, v_temp, M, C, RTT, compute_power, B)
                proc_cost = compute_processing_cost(n_temp, h, B, RTT, k, M, C)

                time_violation = any(
                    T_total[i][j] > max_delay for j in range(10) if n_temp[i][j] > 0
                )
                cost_violation = any(
                    proc_cost[i][j] > max_cost for j in range(10) if n_temp[i][j] > 0
                )

                if time_violation or cost_violation:
                    continue

                score = get_total_score_for_i(i, n_temp, v_temp, M, C, RTT, compute_power, B, h, k, w_time, w_cost)

                if score < best_score:
                    best_score = score
                    best_alloc = temp
                    improved = True
                    break
            if improved:
                break

    return best_alloc



def game_theoretic_scheduler(n, v, M, C, RTT, compute_power, B, h, k, max_iter=10, w_time=0.7, w_cost=0.3):

    flag = 0
    round_num = 0

    while flag < 10 and round_num < max_iter:
        print(f"\n🔁 第 {round_num + 1} 轮迭代")
        
        updated = False

        for i in range(10):  # 每个数据中心依次作为博弈方
            current_n_i = n[i].copy()
            print(current_n_i)
            N_i = sum(n[i])

            best_n_i = find_best_fast(i, n, M, C, RTT, compute_power, B, h, k, w_time, w_cost)

            if best_n_i != current_n_i:
                n[i] = best_n_i
                updated = True
            if updated:
                flag = 0
            else:
                flag += 1
                print(f"✅ 当前数据中心未变化，连续稳定次数 flag = {flag}")
        v = update_v_from_n(n)  # 每轮更新资源比例
        round_num += 1

    print("\n✅ 达到收敛条件，迭代结束，共迭代轮数：", round_num)
    return n, v


def save_result_to_txt(n, N, path='./results/'):
    # 创建目录（若不存在）
    os.makedirs(path, exist_ok=True)

    # 文件名如：N_2-0-0-0-8-...-n.txt
    N_name = '-'.join(str(x) for x in N)
    filename = f"N_{N_name}-n.txt"
    filepath = os.path.join(path, filename)

    # 写入文件
    with open(filepath, 'w') as f:
        f.write("任务卸载矩阵 n[i][j]：\n")
        for i in range(10):
            line = ' '.join(str(n[i][j]) for j in range(10))
            f.write(f"{line}\n")

    print(f"结果已保存至: {filepath}")




if __name__ == "__main__":

    #数据中心10个其中北京为DC1~DC4，成都为DC5~DC8，广州为DC9~DC10

    RTT = build_rtt_matrix()    #10*10的矩阵，RTT[i][j]为Regioni和DCj之间的RTT时延
    Bw = build_Bw_matrix()      #10*10的矩阵，Bw[i][j]为Regioni和DCj之间的Bw带宽
    k =  build_computation_cost()    #k[j]为数据中心j的计算成本
    h = build_transmission_cost()    #h[i][j]为区域i与数据中心j之间的传输成本
    compute_power, memory_capacity = build_dc_resources()   ##数据中心j的计算能力和内存大小

    svc1 = Service(name="svc1", M=220, C=74, max_delay=5, max_cost=10, memory=8)        # 创建服务实例
    n, v = initialize_decision_variables()      #创建服务策略、资源策略核心变量
    N = [100,100,100,100,100,100,100,100,100,100]    #定义各区域的任务需求N
        # [15,3,3,3,3,3,3,3,3,3]15,0,0,0,0,0,0,3,0,0
        # [150, 300, 20, 7, 9, 13, 8, 6, 15, 24]
    #初始化定义自身任务和资源状态
    for i in range(0,10):
        n[i][i] = N[i]  # 所有任务初始化自己处理
        v[i][i] = 1.0   # 所有资源初始化自己承担

    final_n, final_v = game_theoretic_scheduler(n, v, svc1.M, svc1.C, RTT, compute_power, Bw, h, k)

    # 输出最终结果
    print("\n=== 最终最优路由策略矩阵 n ===")
    for i in range(10):
        print(f"Region{i} →", final_n[i])
    print("\n=== 最终最优资源分配矩阵 n ===")
    for i in range(10):
        print(f"dc{i} →", final_v[i])

    save_result_to_txt(final_n, N, path='D:\\Users\\zhy\\Desktop\\Srvcast\\test\\test5_routing-table\\data')

    # best_n0 = find_best_fast(0, n, svc1.M, svc1.C, RTT, compute_power, Bw, h, k)
    # print("最优组合 n[0] =", best_n0)


    # n[0][:] = [1,1,1,0,0,0,0,0,0,0]
    # v = update_v_from_n(n)
    # print(n[0])
    # print(v[0])

    # n[6][0] = 8    
    # v = update_v_from_n(n)
    
    # print("v[0][i] (dc0 向每个 dc 分配的资源比例):")
    # for i in range(10):
    #     print(f"v[i][{0}] = {v[i][0]:.4f}")
        #P_score = P_score(n, proc_time, proc_cost, 0.7, 0.3)
    # proc_time = processing_times(n, v, svc1.M, svc1.C, RTT, compute_power, Bw)
    # proc_cost = compute_processing_cost(n, h, Bw, RTT, k, svc1.M, svc1.C)

    # sum = get_total_score_for_i(0, n, v, svc1.M, svc1.C, RTT, compute_power, Bw, h, k, w_time=0.7, w_cost=0.3)
    # print(sum)
    #print_all_processing_results(n, proc_time, proc_cost, P_score)

    # 博弈收敛标志位、迭代轮次以及最大迭代轮次
    # 执行迭代博弈调度