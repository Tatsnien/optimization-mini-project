# import sys
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

# sys.stdin = open("input10.txt")


# Point: 100
# Submit ID: f3828e
class Ortools:
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

    def tsp_by_ortools(self):
        manager = pywrapcp.RoutingIndexManager(len(self.d), 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return self.d[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            index = routing.Start(0)
            res = []
            while not routing.IsEnd(index):
                res.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            res = res[1:]
            return solution.ObjectiveValue(), res
        else:
            return -1

    # Start from optimal solution of TSP, cutting nodes until convergent
    def solve(self):
        cur_dist, cur_state = self.tsp_by_ortools()
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


solver = Ortools()
result = solver.solve()