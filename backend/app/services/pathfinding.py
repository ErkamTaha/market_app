"""
A* Pathfinding Service
======================
Finds the shortest walkable path between two points on the market map.

How it works:
1. The map is converted to a grid (e.g., 100x60 cells)
2. Shelves and walls are marked as obstacles (can't walk through)
3. Aisles, entrance, and checkout are walkable
4. A* algorithm finds the shortest path avoiding obstacles
5. The path is simplified (unnecessary intermediate points removed)

A* is like Dijkstra's algorithm but smarter — it uses a heuristic
(estimated distance to goal) to explore promising directions first,
making it much faster for 2D grid pathfinding.
"""
import heapq
import math


# Map dimensions (our coordinate system)
MAP_WIDTH = 100
MAP_HEIGHT = 60

# Cell size for the pathfinding grid (smaller = more accurate, slower)
CELL_SIZE = 1

# Walking speed in map units per second (for time estimates)
# Assuming 1 map unit ≈ 0.3 meters, walking at 1.2 m/s
WALKING_SPEED = 4.0  # map units per second


def build_obstacle_grid(zones):
    """
    Convert map zones into a boolean grid.
    True = obstacle (can't walk), False = walkable.

    Only shelves and walls are obstacles.
    Everything else (aisles, entrance, checkout, empty space) is walkable.
    """
    grid_w = int(MAP_WIDTH / CELL_SIZE)
    grid_h = int(MAP_HEIGHT / CELL_SIZE)

    # Start with everything walkable
    grid = [[False] * grid_w for _ in range(grid_h)]

    for zone in zones:
        if zone.zone_type in ("shelf", "wall"):
            # Mark all cells covered by this zone as obstacles
            x_start = max(0, int(zone.x / CELL_SIZE))
            y_start = max(0, int(zone.y / CELL_SIZE))
            x_end = min(grid_w, int((zone.x + zone.width) / CELL_SIZE))
            y_end = min(grid_h, int((zone.y + zone.height) / CELL_SIZE))

            for gy in range(y_start, y_end):
                for gx in range(x_start, x_end):
                    grid[gy][gx] = True

    return grid


def heuristic(a, b):
    """Euclidean distance heuristic for A*."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def astar(grid, start, goal):
    """
    A* pathfinding on a 2D grid.

    Parameters:
        grid: 2D list of booleans (True = obstacle)
        start: (x, y) tuple in grid coordinates
        goal: (x, y) tuple in grid coordinates

    Returns:
        List of (x, y) tuples representing the path, or empty list if no path found.
    """
    grid_h = len(grid)
    grid_w = len(grid[0]) if grid_h > 0 else 0

    # Clamp start and goal to grid bounds
    sx = max(0, min(start[0], grid_w - 1))
    sy = max(0, min(start[1], grid_h - 1))
    gx = max(0, min(goal[0], grid_w - 1))
    gy = max(0, min(goal[1], grid_h - 1))

    start = (sx, sy)
    goal = (gx, gy)

    # If start or goal is inside an obstacle, find nearest walkable cell
    if grid[sy][sx]:
        start = find_nearest_walkable(grid, sx, sy)
        if not start:
            return []

    if grid[gy][gx]:
        goal = find_nearest_walkable(grid, gx, gy)
        if not goal:
            return []

    # A* algorithm
    # Priority queue: (f_score, x, y)
    open_set = [(0, start[0], start[1])]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    # 8 directions: horizontal, vertical, and diagonal
    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]

    while open_set:
        _, cx, cy = heapq.heappop(open_set)
        current = (cx, cy)

        if current == goal:
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy

            # Bounds check
            if nx < 0 or nx >= grid_w or ny < 0 or ny >= grid_h:
                continue

            # Obstacle check
            if grid[ny][nx]:
                continue

            # Diagonal movement: also check the two adjacent cells
            # to prevent cutting through wall corners
            if dx != 0 and dy != 0:
                if grid[cy][cx + dx] or grid[cy + dy][cx]:
                    continue

            neighbor = (nx, ny)
            # Diagonal movement costs more (√2 ≈ 1.414)
            move_cost = 1.414 if (dx != 0 and dy != 0) else 1.0
            tentative_g = g_score[current] + move_cost

            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], nx, ny))

    return []  # No path found


def find_nearest_walkable(grid, x, y):
    """Find the nearest walkable cell to (x, y) using BFS."""
    grid_h = len(grid)
    grid_w = len(grid[0])
    visited = set()
    queue = [(x, y)]
    visited.add((x, y))

    while queue:
        cx, cy = queue.pop(0)
        if 0 <= cx < grid_w and 0 <= cy < grid_h and not grid[cy][cx]:
            return (cx, cy)

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) not in visited and 0 <= nx < grid_w and 0 <= ny < grid_h:
                visited.add((nx, ny))
                queue.append((nx, ny))

    return None


def simplify_path(path):
    """
    Remove unnecessary intermediate points from the path.
    If three consecutive points are on the same line, the middle one is redundant.
    This reduces the path from potentially hundreds of points to just the turns.
    """
    if len(path) <= 2:
        return path

    simplified = [path[0]]

    for i in range(1, len(path) - 1):
        prev = path[i - 1]
        curr = path[i]
        next_pt = path[i + 1]

        # Check if direction changed
        dx1 = curr[0] - prev[0]
        dy1 = curr[1] - prev[1]
        dx2 = next_pt[0] - curr[0]
        dy2 = next_pt[1] - curr[1]

        if dx1 != dx2 or dy1 != dy2:
            simplified.append(curr)

    simplified.append(path[-1])
    return simplified


def find_path(zones, from_x, from_y, to_x, to_y):
    """
    Main entry point: find a path between two map coordinates.

    Returns:
        dict with 'waypoints' (list of {x, y}), 'distance', 'estimated_seconds'
    """
    grid = build_obstacle_grid(zones)

    # Convert map coordinates to grid coordinates
    start = (int(from_x / CELL_SIZE), int(from_y / CELL_SIZE))
    goal = (int(to_x / CELL_SIZE), int(to_y / CELL_SIZE))

    raw_path = astar(grid, start, goal)

    if not raw_path:
        return {"waypoints": [], "distance": 0, "estimated_seconds": 0}

    # Simplify and convert back to map coordinates
    simplified = simplify_path(raw_path)
    waypoints = [{"x": p[0] * CELL_SIZE, "y": p[1] * CELL_SIZE} for p in simplified]

    # Calculate total distance
    total_distance = 0
    for i in range(1, len(simplified)):
        dx = simplified[i][0] - simplified[i - 1][0]
        dy = simplified[i][1] - simplified[i - 1][1]
        total_distance += math.sqrt(dx * dx + dy * dy) * CELL_SIZE

    estimated_seconds = int(total_distance / WALKING_SPEED)

    return {
        "waypoints": waypoints,
        "distance": round(total_distance, 1),
        "estimated_seconds": max(1, estimated_seconds)
    }
