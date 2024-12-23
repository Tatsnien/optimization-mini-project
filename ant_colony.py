import random

# Point: 70
# Submit ID: 68b9fd

class ACO:
    def __init__(self, bestRoute, minCost, costs, nbAnts: int, generations: int, alpha: float, beta: float, rho: float):
        self.bestRoute = bestRoute
        self.minCost = minCost
        self.costs = costs
        self.nbVers = len(costs)
        self.nbAnts = nbAnts
        self.generations = generations
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.ants = []
        self.pheromone = [[1/(self.nbVers**2) for _ in range(self.nbVers)] for _ in range(self.nbVers)]
        self.solution = {}

    def update_pheromone(self):
        for ant in self.ants:
            ant.update_pheromone_delta()
        for i in range(self.nbVers):
            for j in range(self.nbVers):
                self.pheromone[i][j] *= self.rho
                for ant in self.ants:
                    self.pheromone[i][j] += ant.pheromoneDelta[i][j]

    def solve(self):
        for _ in range(self.generations):
            self.ants = [Ant(self) for _ in range(self.nbAnts)]
            for ant in self.ants:
                ant.construct_route()
                if ant.totalCost < self.minCost:
                    self.minCost = ant.totalCost
                    self.bestRoute = ant.route
                    print(f"Update the best: {self.minCost}")
            self.update_pheromone()
            zeroIndex = self.bestRoute.index(0)
        self.solution["best route"] = self.bestRoute[zeroIndex:] + self.bestRoute[:zeroIndex] + [0]
        self.solution["min cost"] = self.minCost

class Ant:
    def __init__(self, aco: ACO):
        self.aco = aco
        self.costs = aco.costs
        self.nbVers = aco.nbVers
        self.eta = [[0 if self.costs[j][i] == 0 else 1 / self.costs[j][i] for i in range(self.nbVers)] for j in range(self.nbVers)]
        self.pheromoneDelta = [[0 for _ in range(self.nbVers)] for _ in range(self.nbVers)]

        self.start = random.randint(0, self.nbVers - 1)
        self.current = self.start
        self.unvisited = [i for i in range(self.nbVers) if i != self.start]
        self.route = [self.start]
        self.totalCost = 0

    def update_pheromone_delta(self):
        for ver in self.route:
            self.pheromoneDelta[ver - 1][ver] = 1 / self.totalCost if self.totalCost != 0 else 0

    def select_probability(self, probabilities: list):
        rand = random.random()
        sum = 0
        index = None
        for i, p in enumerate(probabilities):
            sum += p
            if sum > rand:
                index = i 
                break
        return index

    def generate_probabilities(self):
        p = [0 for _ in range(self.nbVers)]
        sum = 0
        for ver in self.unvisited:
            sum += (self.aco.pheromone[self.current][ver]**self.aco.alpha) * (self.eta[self.current][ver]**self.aco.beta)
        for ver in self.unvisited:
            p[ver] = (self.aco.pheromone[self.current][ver]**self.aco.alpha) * (self.eta[self.current][ver]**self.aco.beta) / sum
        return p

    def find_next(self):
        p = self.generate_probabilities()
        sel = self.select_probability(p)
        self.route.append(sel)
        self.unvisited.remove(sel)
        self.totalCost += self.costs[self.current][sel]
        self.current = sel

    def construct_route(self):
        for _ in range(self.nbVers - 1):
            self.find_next()
        self.totalCost += self.costs[self.current][self.start]

class NearestNeighbor:
    def __init__(self, distanceMatrix, amount, order):
        self.costs = distanceMatrix
        self.amount = transpose(amount)
        self.order = order
        self.solution = {}

    def solve(self):
        order = self.order.copy()
        current = 0
        bestRoute = [0]
        unvisited = [i for i in range(1, len(self.costs))]
        totalCost = 0
        while True:
            minCost = float("inf")
            nextVer = None
            for ver in unvisited:
                if self.costs[current][ver] < minCost:
                    minCost = self.costs[current][ver]
                    nextVer = ver
            totalCost += minCost
            bestRoute.append(nextVer)
            unvisited.remove(nextVer)
            order = add(order, self.amount[nextVer - 1], subtract=True)
            current = nextVer
            
            if max(order) <= 0:
                break

        excessAmount = [0 - i for i in self.order]
        for ver in bestRoute:
            if ver != 0:
                excessAmount = add(excessAmount, self.amount[ver - 1])
        for ver in bestRoute + [0]:
            if ver == 0:
                continue
            if min(add(excessAmount, self.amount[ver - 1], subtract=True)) < 0:
                continue
            verIndex = bestRoute.index(ver)
            previous = bestRoute[verIndex - 1]
            following = bestRoute[verIndex + 1]
            totalCost -= self.costs[previous][ver] + self.costs[ver][following] - self.costs[previous][following]
            bestRoute.remove(ver)
            excessAmount = add(excessAmount, self.amount[ver - 1], subtract=True)

        self.solution = {"best route": bestRoute, "total cost": totalCost}

class OrderPickingUpRouteSolver:
    def __init__(self, distanceMatrix, amount, order: list, nbAnts: int = 20, generations: int = 5, alpha: float = 1, beta: float = 1, rho: float = 0.5):
        self.costs = distanceMatrix
        self.heuristicSolver = NearestNeighbor(distanceMatrix, amount, order)
        self.acoConfig = {
            "nbAnts": nbAnts,
            "generations": generations,
            "alpha": alpha,
            "beta": beta,
            "rho": rho
        }

    def solve(self):
        self.heuristicSolver.solve()
        bestRoute = self.heuristicSolver.solution["best route"]
        n = len(bestRoute)
        routeMapping = {i: bestRoute[i] for i in range(n)}
        self.acoConfig["bestRoute"] = [i for i in range(n)]
        self.acoConfig["minCost"] = self.heuristicSolver.solution["total cost"]
        self.acoConfig["costs"] = [[self.costs[routeMapping[j]][routeMapping[i]] for i in range(len(bestRoute))] for j in range(len(bestRoute))]
        aco = ACO(**self.acoConfig)
        aco.solve()
        bestRoute = [routeMapping[i] for i in aco.solution["best route"]]
        totalCost = aco.solution["min cost"]
        bestRoute = bestRoute[1:-1]
        print(str(len(bestRoute)) + f"\n{' '.join([str(i) for i in bestRoute])}")

def transpose(matrix):
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]

def add(list1, list2, subtract=False):
    k = -1 if subtract else 1
    return [list1[i] + list2[i] * k for i in range(len(list1))]


def main():
    N, M = map(int, input().split())
    Q = [list(map(int, input().split())) for _ in range(N)]
    d = [list(map(int, input().split())) for _ in range(M + 1)]
    q = list(map(int, input().split()))

    opur = OrderPickingUpRouteSolver(d, Q, q)
    opur.solve()

if __name__ == "__main__":
    main()