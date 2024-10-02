class Node:
    def __init__(self, x, y, ecost=0, scost=0, parent=None, action=None, treasures=None, trap_emultiplier=1, trap_smultiplier=1):
        self.x = x
        self.y = y
        self.ecost = ecost
        self.scost = scost
        self.parent = parent
        self.action = action
        self.treasures = treasures if treasures is not None else set()
        self.trap_emultiplier = trap_emultiplier
        self.trap_smultiplier = trap_smultiplier
        self.hcost = 0  # Heuristic cost

def Hypotenuse_distance(x1, y1, x2, y2):
    if y2 % 2 != 0:  # odd
        return (((x2 - x1 - 0.5) ** 2) + ((y2 - y1) ** 2)) ** 0.5
    else:  # even
        return (((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5

def transition_model(node, action):
    if node.y % 2 != 0:  # odd row
        directions = {
            "N": (-1, 0), "NE": (-1, 1), "SE": (0, 1),
            "S": (1, 0), "SW": (0, -1), "NW": (-1, -1)
        }
    else:  # even row
        directions = {
            "N": (-1, 0), "NE": (0, 1), "SE": (1, 1),
            "S": (1, 0), "SW": (1, -1), "NW": (0, -1)
        }
    dx, dy = directions[action]
    new_x, new_y = node.x + dx, node.y + dy
    return new_x, new_y

def append_and_sort(frontier, node):
    duplicated = False
    removed = False
    for i, f in enumerate(frontier):
        if (f.x, f.y, f.treasures) == (node.x, node.y, node.treasures):
            duplicated = True
            if f.ecost + f.hcost > node.ecost + node.hcost:
                del frontier[i]
                removed = True
                break
    if (not duplicated) or removed:
        insert_index = len(frontier)
        for i, f in enumerate(frontier):
            if f.ecost + f.hcost > node.ecost + node.hcost:
                insert_index = i
                break
        frontier.insert(insert_index, node)
    return frontier

def is_valid(x, y, grid):
    if 0 <= x < len(grid) and 0 <= y < len(grid[0]):
        return grid[x][y] not in ["Obstacle", "Trap 4"]
    return False

def get_node_state(node):
    return (node.x, node.y, frozenset(node.treasures))

def reconstruct_path(node):
    path = []
    while node:
        path.append((node.x, node.y, f"energy {node.ecost}", f"steps {node.scost}"))
        if node.action:
            path.append(f"Moved {node.action}")
        node = node.parent
    path.reverse()
    return path

def handle_traps_and_rewards(child, grid):
    if grid[child.x][child.y] == "Trap 1":  # energy
        child.trap_emultiplier *= 2
    elif grid[child.x][child.y] == "Trap 2":  # step
        child.trap_smultiplier *= 2
    elif grid[child.x][child.y] == "Trap 3":
        for _ in range(2):  # force 2 steps in the same direction
            new_x, new_y = transition_model(child, child.action)
            if is_valid(new_x, new_y, grid):
                child.x, child.y = new_x, new_y
                child.ecost += 1
                child.scost += 1
            else:
                break
    elif grid[child.x][child.y] == "Trap 4":
        child.trap_emultiplier *= 99999999  # Discourage expansion of such node
    elif grid[child.x][child.y] == "Reward 1":
        child.trap_emultiplier *= 0.5
    elif grid[child.x][child.y] == "Reward 2":  # step
        child.trap_smultiplier *= 0.5
    elif grid[child.x][child.y] == "Treasure":
        child.treasures.add((child.x, child.y))

def a_star(initial_node, grid):
    frontier = [initial_node]
    explored = set()

    while frontier:
        current_node = frontier.pop(0)
        explored.add(get_node_state(current_node))

        if len(current_node.treasures) == 4:
            return reconstruct_path(current_node)

        for action in ["N", "NE", "SE", "S", "SW", "NW"]:
            new_x, new_y = transition_model(current_node, action)
            if is_valid(new_x, new_y, grid):
                new_ecost = current_node.ecost + 1 * current_node.trap_emultiplier
                new_scost = current_node.scost + 1 * current_node.trap_smultiplier
                new_treasures = set(current_node.treasures)
                new_trap_emultiplier = current_node.trap_emultiplier
                new_trap_smultiplier = current_node.trap_smultiplier

                child = Node(new_x, new_y, new_ecost, new_scost, current_node, action, new_treasures, new_trap_emultiplier, new_trap_smultiplier)
                handle_traps_and_rewards(child, grid)

                min_distance = float('inf')
                for treasure in [(x, y) for x in range(len(grid)) for y in range(len(grid[0])) if grid[x][y] == "Treasure"]:
                    if treasure not in child.treasures:
                        distance = Hypotenuse_distance(child.x, child.y, treasure[0], treasure[1])
                        if distance < min_distance:
                            min_distance = distance
                child.hcost = min_distance

                if get_node_state(child) not in explored:
                    frontier = append_and_sort(frontier, child)

    return []

if __name__ == "__main__":
    grid = [
        [None, None, None, None, "Reward 1", None, None, None, None, None],
        [None, "Trap 2", None, "Trap 1", "Treasure", None, "Trap 3", None, "Obstacle", None],
        [None, None, "Obstacle", None, "Obstacle", None, None, "Reward 2", "Trap 1", None],
        ["Obstacle", "Reward 1", None, "Obstacle", None, "Trap 3", "Obstacle", "Treasure", None, "Treasure"],
        [None, None, "Trap 2", "Treasure", "Obstacle", None, "Obstacle", "Obstacle", None, None],
        [None, None, None, None, None, "Reward 2", None, None, None, None]
    ]

    initial_node = Node(0, 0)
    path = a_star(initial_node, grid)
    print("Full Path (coordinates and actions):")
    for step in path:
        print(step)
