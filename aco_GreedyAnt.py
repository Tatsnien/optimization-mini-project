import random

# Point: 95
# Submit ID: 51098e

class ACO:
    def __init__(self, costs, Q, q, nbAnts: int, generations: int, alpha: float = 1, beta: float = 2, p: float = 0.1):
        self.costs = costs
        self.Q = Q
        self.q = q
        self.nbVers = len(costs)
        self.nbAnts = nbAnts
        self.generations = generations
        self.alpha = alpha
        self.beta = beta
        self.p = p
        self.ants = [GreedyAnt(self)]
        self.pheromone = [[1 / (self.nbVers ** 2) for _ in range(self.nbVers)] for _ in range(self.nbVers)]

    def update_pheromone(self):
        for ant in self.ants:
            ant.update_pheromone_delta()
        for i in range(self.nbVers):
            for j in range(self.nbVers):
                self.pheromone[i][j] *= 1 - self.p
                for ant in self.ants:
                    self.pheromone[i][j] += ant.pheromoneDelta[i][j]

    def solve(self):
        bestRoute = None
        minCost = float("inf")
        count = 0
        updated = False
        for g in range(self.generations + 1):
            if g != 0:
                self.ants = [Ant(self) for _ in range(self.nbAnts)]
            for ant in self.ants:
                ant.construct_route()
                if ant.totalCost < minCost:
                    minCost = ant.totalCost
                    bestRoute = ant.route
                    updated = True
            self.update_pheromone()
            del self.ants
            if updated:
                count = 0
                updated = False
            else:
                count += 1
            if count == self.generations // 5:
                break
        zeroIndex = bestRoute.index(0)
        bestRoute = [bestRoute[zeroIndex - i] for i in range(1, len(bestRoute))]
        print(str(len(bestRoute)), " ".join(map(str, bestRoute)), sep="\n")


class Ant:
    def __init__(self, aco: ACO):
        self.aco = aco
        self.costs = aco.costs
        self.Q = aco.Q
        self.q = aco.q
        self.nbVers = aco.nbVers
        self.nbProducts = len(self.q)
        # self.eta = [[0 if self.costs[j][i] == 0 else 1 / self.costs[j][i] for i in range(self.nbVers)] for j in range(self.nbVers)]
        self.pheromoneDelta = [[0 for _ in range(self.nbVers)] for _ in range(self.nbVers)]

        self.start = random.randint(0, self.nbVers - 1)
        self.current = self.start
        self.unvisited = [i for i in range(self.nbVers) if i != self.start]
        self.route = [self.start]
        self.totalCost = 0

        self.current_load = [0 for _ in range(self.nbProducts)]
        self.update_current_load()

    def update_current_load(self):
        for i in range(self.nbProducts):
            self.current_load[i] += self.Q[i][self.current]

    def satisfy_capacity(self):
        for i in range(self.nbProducts):
            if self.current_load[i] < self.q[i]:
                return False
        return True

    def update_pheromone_delta(self):
        for ver in self.route:
            self.pheromoneDelta[ver - 1][ver] = 1 / self.totalCost if self.totalCost != 0 else 0

    def select_probability(self, probabilities: list):
        rand = random.random()
        sum = 0
        index = None
        for i, p in enumerate(probabilities):
            sum += p
            if sum >= rand:
                index = i
                break
        return index

    def generate_probabilities(self):
        p = [0 for _ in range(self.nbVers)]
        sum = 0
        for ver in self.unvisited:
            sum += (self.aco.pheromone[self.current][ver] ** self.aco.alpha) * (
                        self.compute_eta(self.current, ver) ** self.aco.beta)
        for ver in self.unvisited:
            p[ver] = (self.aco.pheromone[self.current][ver] ** self.aco.alpha) * (
                        self.compute_eta(self.current, ver) ** self.aco.beta) / sum
        return p

    def compute_eta(self, i, j):
        return 1 / self.costs[i][j] if self.costs[i][j] != 0 else 0

    def find_next(self):
        p = self.generate_probabilities()
        sel = self.select_probability(p)
        self.move_to_next_ver(sel)

    def move_to_next_ver(self, ver):
        self.route.append(ver)
        self.unvisited.remove(ver)
        self.totalCost += self.costs[self.current][ver]
        self.current = ver

    def construct_route(self):
        for _ in range(self.nbVers - 1):
            self.find_next()
            self.update_current_load()
            if self.satisfy_capacity():
                break
        if 0 not in self.route:
            self.move_to_next_ver(0)
        self.totalCost += self.costs[self.current][self.start]

class GreedyAnt(Ant):
    def __init__(self, aco: ACO):
        super().__init__(aco)

    def find_next(self):
        sel = self.select_nearest()
        self.move_to_next_ver(sel)

    def select_nearest(self):
        min_cost = float("inf")
        sel = -1
        for ver in self.unvisited:
            if self.costs[self.current][ver] < min_cost:
                min_cost = self.costs[self.current][ver]
                sel = ver
        return sel

if __name__ == "__main__":
    N, M = [int(x) for x in input().split()]
    Q = [[0] + [int(x) for x in input().split()] for _ in range(N)]
    d = [[int(x) for x in input().split()] for _ in range(M + 1)]
    q = [int(x) for x in input().split()]

    nbAnts = min(M + 1, 50)
    aco = ACO(d, Q, q, nbAnts=nbAnts, generations=15, alpha=1, beta=5)
    aco.solve()