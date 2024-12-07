# import sys
import time
import random

# sys.stdin = open("input10.txt")


# Point: 100
# Submit ID: 23b2be
class Opt2:
    def __init__(self, n=None, m=None, Q=None, d=None, q=None):
        if not n:
            n, m = map(int, input().strip().split())
            Q = [[0] * (m + 1)]
            for _ in range(n):
                Q.append([0] + [int(i) for i in input().strip().split()])
            d = [[int(j) for j in input().strip().split()] for i in range(m + 1)]
            q = [0] + [int(i) for i in input().strip().split()]

        self.time_limit = 5 * 60
        self.n = n
        self.m = m
        self.Q = Q
        self.d = d
        self.q = q

    def dist_of_path(self, path):
        res = self.d[0][path[0]]
        cur_path = path + [0]
        for i in range(1, len(cur_path)):
            res += self.d[cur_path[i]][cur_path[i - 1]]
        return res

    @staticmethod
    def print_solution(state):
        print(len(state) - 2)
        for i in state[1: -1]:
            print(i, end=' ')

    def loaded_list(self, state):
        load = [0] * (self.n + 1)
        for node in state:
            for item in range(self.n + 1):
                load[item] += self.Q[item][node]
        return load

    def loaded_list_remove_node(self, node, load):
        return [load[i] - self.Q[i][node] for i in range(1, self.n + 1)]

    def satisfy_constraint(self, load):
        for i in range(self.n + 1):
            if load[i] < self.q[i]:
                return False
        return True

    def tsp_by_greedy(self):
        cur_state = []
        cur_node = 0
        cur_dist = 0
        for _ in range(self.m):
            new_node = -1
            new_dist = -1
            for i in range(1, self.m + 1):
                if i in cur_state:
                    continue
                if new_node == -1 or self.d[cur_node][i] < new_dist:
                    new_node = i
                    new_dist = self.d[cur_node][new_node]
            cur_dist += new_dist
            cur_state.append(new_node)
            cur_node = new_node
        cur_dist += self.d[cur_node][0]
        return cur_dist, cur_state

    def tsp_by_opt_2(self):
        cur_dist, cur_state = self.tsp_by_greedy()
        cur_state = [0] + cur_state + [0]
        cnt = 20

        def swap(state, idx1, idx2):
            while idx1 < idx2:
                temp = state[idx1]
                state[idx1] = state[idx2]
                state[idx2] = temp
                idx1 += 1
                idx2 -= 1

        def dist_after_swap(idx1, idx2):
            p = cur_state[idx1]
            q = cur_state[idx2]
            pre_p = cur_state[idx1 - 1]
            next_q = cur_state[idx2 + 1]
            return cur_dist - self.d[pre_p][p] - self.d[q][next_q] + self.d[pre_p][q] + self.d[p][next_q]

        def get_neighbor():
            nonlocal cur_state, cur_dist
            neighbor = (-1, -1)

            for i in range(1, self.m):
                for j in range(1, i):
                    new_dist = dist_after_swap(j, i)
                    if neighbor[0] == -1 and new_dist < cur_dist or new_dist < neighbor[0]:
                        swap(cur_state, j, i)
                        neighbor = (new_dist, cur_state)

            return neighbor

        def has_next_state():
            nonlocal cur_dist, cur_state
            next_dist, next_state = get_neighbor()

            if next_state == -1:
                return False
            else:
                cur_dist = next_dist
                cur_state = next_state
                return True

        start_time = time.time()
        while time.time() - start_time < self.time_limit:
            if not has_next_state():
                break
        return cur_dist, cur_state[1: -1]

    # Start from optimal solution of TSP, cutting nodes until convergent
    def solve(self):
        cur_dist, cur_state = self.tsp_by_opt_2()
        cur_state = [0] + cur_state + [0]
        cur_load = self.loaded_list(cur_state)

        def removable(idx):
            return self.satisfy_constraint([cur_load[i] - self.Q[i][cur_state[idx]] for i in range(self.n + 1)])

        def get_neighbor():
            nonlocal cur_dist, cur_load, cur_state
            neighbor = (-1, -1, -1)  # (dist, state, load)

            for idx, node in enumerate(cur_state):
                if node == 0 or not removable(idx):
                    continue

                load = [cur_load[i] - self.Q[i][node] for i in range(self.n + 1)]

                state = cur_state[:]
                state.pop(idx)

                pre_node = cur_state[idx - 1]
                next_node = cur_state[idx + 1]
                dist = cur_dist - self.d[pre_node][node] - self.d[node][next_node] + self.d[pre_node][next_node]

                if neighbor[0] == -1 or dist < neighbor[0]:
                    neighbor = (dist, state, load)

            return neighbor

        def has_next_state():
            nonlocal cur_dist, cur_load, cur_state
            next_dist, next_state, next_load = get_neighbor()

            if next_state == -1:
                return False
            else:
                cur_dist = next_dist
                cur_state = next_state
                cur_load = next_load
                return True

        while True:
            if not has_next_state():
                break

        self.print_solution(cur_state)
        return cur_dist, cur_state, cur_load


solver = Opt2()
solver.solve()
