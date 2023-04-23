import heapq
from math import floor
from state import State
from sys import stderr

class Dijkstra:
    def __init__(self, graph, start):
        self.graph = graph
        self.start = start
        self.distances = None
        self.visited = None

    def shortest_path(self):
        rows = len(self.graph)
        cols = len(self.graph[0])
        self.distances = [[float('inf') for j in range(cols)] for i in range(rows)]
        self.distances[self.start[0]][self.start[1]] = 0
        self.visited = [[False for j in range(cols)] for i in range(rows)]
        heap = [(0, self.start)]

        while heap:
            curr_dist, curr_node = heapq.heappop(heap)
            curr_row, curr_col = curr_node

            if self.visited[curr_row][curr_col]:
                continue

            self.visited[curr_row][curr_col] = True

            for neighbor in self.get_neighbors(curr_row, curr_col):
                neighbor_row, neighbor_col = neighbor
                if self.visited[neighbor_row][neighbor_col]:
                    continue
                if self.graph[neighbor_row][neighbor_col]:
                    new_dist = curr_dist + 1
                    if new_dist < self.distances[neighbor_row][neighbor_col]:
                        self.distances[neighbor_row][neighbor_col] = new_dist
                        heapq.heappush(heap, (new_dist, neighbor))

        return self.distances

    def get_neighbors(self, row, col):
        neighbors = []
        rows = len(self.graph)
        cols = len(self.graph[0])
        if row > 0:
            neighbors.append((row-1, col))
        if row < rows - 1:
            neighbors.append((row+1, col))
        if col > 0:
            neighbors.append((row, col-1))
        if col < cols - 1:
            neighbors.append((row, col+1))
        return neighbors


class Assigner:
    def __init__(self, initial_state: State):
        self.state = initial_state

    def assign_tasks_to_agent(self, agent) -> list:
        n_rows, n_cols = len(State.goals), len(State.goals[0])
        agent_color = State.agent_colors[agent]
        letters = [chr(ord('A') + i) for i in range(26) if State.box_colors[i] == agent_color]
        boxes = {}
        for letter in letters:
            boxes[letter] = [(row, col) for row in range(n_rows) for col in range(n_cols) if self.state.boxes[row][col] == letter]
        goals = {}
        for letter in letters + [chr(ord('0') + agent)]:
            goals[letter] = [(row, col) for row in range(n_rows) for col in range(n_cols) if State.goals[row][col] == letter]

        print(f"Agent {agent} boxes: {boxes}", file=stderr, flush=True)
        print(f"Agent {agent} goals: {goals}", file=stderr, flush=True)

    def assign_tasks(self) -> dict:
        tasks = dict()
        n_agents = len(self.state.agent_rows)
        for agent in range(n_agents):
            tasks[agent] = self.assign_tasks_to_agent(agent)
        return tasks
