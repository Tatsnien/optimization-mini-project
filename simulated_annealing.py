#PYTHON 
import random
import math

# Point: 59
# Submit ID: 3c4cb9


# Read input values
N, M = map(int, input().split())
Q = [list(map(int, input().split())) for _ in range(N)]
d = [list(map(int, input().split())) for _ in range(M + 1)]
q = list(map(int, input().split()))

# Initialize variables
def initialize_greedy_path():
    # Create a list of shelves sorted by the total quantity needed
    total_quantities = [sum(Q[i][j] for i in range(N)) for j in range(M)]
    sorted_shelves = sorted(range(M), key=lambda x: -total_quantities[x])
    return sorted_shelves

def compute_total_distance_and_quantities(path):
    total_distance = d[0][path[0] + 1]  # Distance from door to first shelf
    quantities_collected = [0] * N

    for i in range(len(path)):
        shelf_index = path[i]
        total_distance += d[path[i - 1] + 1][shelf_index + 1] if i > 0 else 0
        for j in range(N):
            quantities_collected[j] += Q[j][shelf_index]  # Collect quantities from the shelf

    total_distance += d[path[-1] + 1][0]  # Return to door
    return total_distance, quantities_collected

def satisfies_quantities(quantities_collected):
    return all(quantities_collected[i] >= q[i] for i in range(N))

def is_better(old_cost, new_cost, temperature):
    if new_cost < old_cost:
        return True
    else:
        return math.exp((old_cost - new_cost) / temperature) > random.random()

def simulated_annealing():
    current_path = initialize_greedy_path()  # Use the greedy initial path
    current_cost, current_quantities = compute_total_distance_and_quantities(current_path)
    best_path = current_path[:]
    best_cost = current_cost

    T = 2000  # Initial temperature
    cooling_rate = 0.95
    max_iterations = 10000

    for iteration in range(max_iterations):
        # Generate a new candidate by swapping two shelves
        new_path = current_path[:]
        l, r = random.sample(range(M), 2)
        new_path[l], new_path[r] = new_path[r], new_path[l]

        new_cost, new_quantities = compute_total_distance_and_quantities(new_path)

        # Accept or reject the new solution based on cost and quantities
        if satisfies_quantities(new_quantities) and is_better(current_cost, new_cost, T):
            current_path = new_path
            current_cost = new_cost
            current_quantities = new_quantities

            # Update best solution
            if current_cost < best_cost:
                best_cost = current_cost
                best_path = current_path

        # Cool down
        T *= cooling_rate

    return best_path, best_cost

# Execute the algorithm
best_path, best_cost = simulated_annealing()

# Prepare output
print(len(best_path))
print(" ".join(str(x + 1) for x in best_path))  # Convert to 1-based index for output

