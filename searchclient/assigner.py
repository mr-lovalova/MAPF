import heapq
from math import floor
from state import State
from sys import stderr


class FloodFill:
    def __init__(self, grid):
        self.grid = grid
        self.reachability_map = [[False] * len(grid[0]) for _ in range(len(grid))]

    def dfs(self, x, y):
        if x < 0 or y < 0 or x >= len(self.grid) or y >= len(self.grid[0]):
            return
        if self.grid[x][y]:
            return
        if self.reachability_map[x][y]:
            return
        self.reachability_map[x][y] = True
        self.dfs(x + 1, y)
        self.dfs(x - 1, y)
        self.dfs(x, y + 1)
        self.dfs(x, y - 1)

    def get_reachability_map(self, position):
        self.reachability_map = [[False] * len(self.grid[0]) for _ in range(len(self.grid))]
        x, y = position
        self.dfs(x, y)
        return self.reachability_map


class Goal:
    def __init__(self, position, letter):
        self.position = position
        self.letter = letter

    def __repr__(self):
        return f"Goal({self.position}, {self.letter})"


class Assigner:
    def __init__(self, initial_state: State):
        self.state = initial_state

    def assign_tasks_to_agent(self, agent) -> tuple:
        n_rows, n_cols = len(State.goals), len(State.goals[0])
        agent_color = State.agent_colors[agent]
        letters = [chr(ord('A') + i) for i in range(26) if State.box_colors[i] == agent_color]
        floodfill = FloodFill(State.walls)
        reachability_map = floodfill.get_reachability_map((self.state.agent_rows[agent], self.state.agent_cols[agent]))
        boxes = {}
        for letter in letters:
            boxes[letter] = [(row, col) for row in range(n_rows) for col in range(n_cols) if self.state.boxes[row][col] == letter and reachability_map[row][col]]
        goals = {}
        for letter in letters + [chr(ord('0') + agent)]:
            goals[letter] = [(row, col) for row in range(n_rows) for col in range(n_cols) if State.goals[row][col] == letter and reachability_map[row][col]]

        # print(f"Agent {agent} boxes: {boxes}", file=stderr, flush=True)
        # print(f"Agent {agent} goals: {goals}", file=stderr, flush=True)
        return boxes, goals

    def build_initial_graph(self, agent):
        tasks = self.assign_tasks_to_agent(agent)[1]
        graph = dict()
        start = Goal("start", None)
        finish = Goal("finish", None)
        graph[start] = set()
        graph[finish] = set()
        for letter in tasks:
            for position in tasks[letter]:
                goal = Goal(position, letter)
                graph[goal] = {finish}
                graph[start].add(goal)
        return graph

    def assign_plans(self) -> dict:
        return [self.build_initial_graph(agent) for agent in range(len(self.state.agent_rows))]
