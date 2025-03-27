from copy import deepcopy

def find_best_fast(i, n, M, C, RTT, compute_power, B, h, k, w_time=0.7, w_cost=0.3, max_try=100):
    N_i = sum(n[i])
    if N_i == 0:
        return n[i]

    current_n_i = n[i][:]
    v_full = update_v_from_n(n)
    current_score = get_total_score_for_i(i, n, v_full, M, C, RTT, compute_power, B, h, k, w_time, w_cost)

    best_score = current_score
    best_alloc = current_n_i[:]

    # ✅ Step 1: 仅尝试前 max_try 个组合
    for idx, alloc in enumerate(generate_task_allocations(N_i)):
        if idx >= max_try:
            break
        if alloc == current_n_i:
            continue

        n_temp = deepcopy(n)
        n_temp[i] = alloc
        v_temp = update_v_from_n(n_temp)
        score = get_total_score_for_i(i, n_temp, v_temp, M, C, RTT, compute_power, B, h, k, w_time, w_cost)

        if score < best_score:
            best_score = score
            best_alloc = alloc[:]

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
                score = get_total_score_for_i(i, n_temp, v_temp, M, C, RTT, compute_power, B, h, k, w_time, w_cost)

                if score < best_score:
                    best_score = score
                    best_alloc = temp
                    improved = True
                    break
            if improved:
                break

    return best_alloc
