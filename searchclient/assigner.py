import collections
from sys import stderr

from state import State

class PathUtils:
    def __init__(self, grid):
        self.grid = grid
        self.reachability_map = [[False] * len(grid[0]) for _ in range(len(grid))]

    def dfs(self, x, y) -> None:
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

    def bfs(self, start, target):
        queue = collections.deque([[start]])
        seen = set([start])

        while queue:
            path = queue.popleft()
            y, x = path[-1]

            if (y, x) == target:
                return path

            for y2, x2 in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= x2 < len(self.grid[0]) and 0 <= y2 < len(self.grid) and not self.grid[y2][x2] and (y2, x2) not in seen:
                    queue.append(path + [(y2, x2)])
                    seen.add((y2, x2))

        return None

    def get_reachability_map(self, position) -> list:
        self.reachability_map = [[False] * len(self.grid[0]) for _ in range(len(self.grid))]
        x, y = position
        self.dfs(x, y)
        return self.reachability_map

    # def extract_goals(self, path) -> list:
    #     goals_encountered = []
    #     for x, y in path:
    #         if self.goals[y][x] != '':
    #             goals_encountered.append(self.goals[y][x])
    #     return goals_encountered
    #
    # def get_goals_on_shortest_path(self, start, target) -> list:
    #     path = self.bfs(start, target)
    #     goals_encountered = self.extract_goals(path)
    #     return goals_encountered


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
        floodfill = PathUtils(State.walls)
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

    def build_initial_graph(self, agent) -> dict:
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

    def get_graph(self, agent) -> dict:
        graph = self.build_initial_graph(agent)
        agent_position = (self.state.agent_rows[agent], self.state.agent_cols[agent])
        path_utils = PathUtils(State.walls)
        print(graph, file=stderr, flush=True)
        for node, neighbours in graph.items():
            path = path_utils.bfs(agent_position, node.position)
            print(f"Agent {agent} path: {path}", file=stderr, flush=True)
        return graph

    def assign_plans(self) -> dict:
        return [self.get_graph(agent) for agent in range(len(self.state.agent_rows))]
