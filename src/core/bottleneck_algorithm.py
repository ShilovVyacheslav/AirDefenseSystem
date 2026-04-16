import math

import numpy as np
from typing import List, Tuple, Optional
from collections import deque
from tqdm import tqdm


class HopcroftKarp:
    def __init__(self, n_left: int, n_right: int, adj: List[List[int]]):
        self.n_left = n_left
        self.n_right = n_right
        self.adj = adj
        self.match_left = [-1] * n_left
        self.match_right = [-1] * n_right
        self.dist = [0] * n_left

    def bfs(self) -> bool:
        queue = deque()
        for u in range(self.n_left):
            if self.match_left[u] == -1:
                self.dist[u] = 0
                queue.append(u)
            else:
                self.dist[u] = float('inf')

        found = False
        while queue:
            u = queue.popleft()
            for v in self.adj[u]:
                nu = self.match_right[v]
                if nu != -1 and self.dist[nu] == float('inf'):
                    self.dist[nu] = self.dist[u] + 1
                    queue.append(nu)
                elif nu == -1:
                    found = True
        return found

    def dfs(self, u: int) -> bool:
        for v in self.adj[u]:
            nu = self.match_right[v]
            if nu == -1 or (self.dist[nu] == self.dist[u] + 1 and self.dfs(nu)):
                self.match_left[u] = v
                self.match_right[v] = u
                return True
        self.dist[u] = float('inf')
        return False

    def max_matching(self) -> int:
        result = 0
        while self.bfs():
            for u in range(self.n_left):
                if self.match_left[u] == -1 and self.dfs(u):
                    result += 1
        return result

    def get_match(self) -> List[int]:
        return self.match_left


def uniq(cost_matrix: np.ndarray) -> List[float]:
    unique_vals = np.unique(cost_matrix)
    return sorted(unique_vals.tolist())


def perfect_matching(threshold: float, cost_matrix: np.ndarray) -> Optional[List[int]]:
    n = cost_matrix.shape[0]
    adj = []

    for i in range(n):
        row_adj = []
        for j in range(n):
            if cost_matrix[i, j] <= threshold:
                row_adj.append(j)
        if not row_adj:
            return None
        adj.append(row_adj)

    hk = HopcroftKarp(n, n, adj)
    if hk.max_matching() < n:
        return None

    return hk.get_match()


def bottleneck_algorithm(cost_matrix: np.ndarray) -> List[Tuple[int, int]]:
    n = cost_matrix.shape[0]
    unique_costs = uniq(cost_matrix)
    total_ops = math.ceil(math.log2(len(unique_costs))) if len(unique_costs) > 1 else 1
    pbar = tqdm(total=total_ops, desc="Bottleneck", unit="step")
    left, right = 0, len(unique_costs) - 1
    best_threshold = unique_costs[-1]
    best_assignment = None
    while left <= right:
        mid = (left + right) // 2
        threshold = unique_costs[mid]
        match = perfect_matching(threshold, cost_matrix)
        pbar.update(1)
        if match is not None:
            best_threshold = threshold
            best_assignment = match
            right = mid - 1
        else:
            left = mid + 1
    pbar.close()
    if best_assignment is None:
        return []
    return [(i, best_assignment[i]) for i in range(n) if best_assignment[i] != -1]