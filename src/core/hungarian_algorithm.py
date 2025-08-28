# core/hungarian.py
import numpy as np


def hungarian_algorithm(cost_matrix):
    n, m = cost_matrix.shape
    A = cost_matrix.copy().astype(float)
    if n > m:
        A = np.hstack([A, np.zeros((n, n - m)) + np.max(A)])
        m = n
    elif m > n:
        A = np.vstack([A, np.zeros((m - n, m)) + np.max(A)])
        n = m

    u = np.zeros(n + 1)
    v = np.zeros(m + 1)
    p = np.zeros(m + 1, dtype=int)
    way = np.zeros(m + 1, dtype=int)

    INF = 10 ** 9

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = np.full(m + 1, INF)
        used = np.zeros(m + 1, dtype=bool)

        while True:
            used[j0] = True
            i0 = p[j0]
            delta = INF
            j1 = 0

            for j in range(1, m + 1):
                if not used[j]:
                    cur = A[i0 - 1, j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j

            for j in range(0, m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta

            j0 = j1
            if p[j0] == 0:
                break

        while j0 != 0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1

    assignment = []
    for j in range(1, m + 1):
        if p[j] != 0:
            i = p[j] - 1
            j_idx = j - 1
            if i < cost_matrix.shape[0] and j_idx < cost_matrix.shape[1]:
                assignment.append((i, j_idx))

    return assignment
