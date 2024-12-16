#PYTHON 
import random

# Read input values
N, M = map(int, input().split())
Q = [list(map(int, input().split())) for _ in range(N)]
d = [list(map(int, input().split())) for _ in range(M + 1)]
q = list(map(int, input().split()))

# Initialize variables
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

def greedy_algorithm():
    path = []
    quantities_collected = [0] * N
    current_shelf = -1  # Start at the door

    while len(path) < M:
        best_shelf = None
        best_distance = float('inf')

        for shelf in range(M):
            if shelf not in path:
                # Calculate distance from current shelf to the next shelf
                distance = d[current_shelf + 1][shelf + 1] if current_shelf != -1 else d[0][shelf + 1]
                if distance < best_distance:
                    best_distance = distance
                    best_shelf = shelf

        if best_shelf is not None:
            path.append(best_shelf)
            current_shelf = best_shelf
            for j in range(N):
                quantities_collected[j] += Q[j][best_shelf]  # Collect quantities from the shelf

    total_distance, quantities_collected = compute_total_distance_and_quantities(path)

    # Check if we satisfy the required quantities
    if satisfies_quantities(quantities_collected):
        return path, total_distance
    else:
        return None, float('inf')  # Return None if we don't satisfy the quantities

# Execute the algorithm
best_path, best_cost = greedy_algorithm()

# Prepare output
if best_path is not None:
    print(len(best_path))
    print(" ".join(str(x + 1) for x in best_path))  # Convert to 1-based index for output
else:
    print("No valid path found.")