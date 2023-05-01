from graphsearch import search
from frontier import FrontierBestFirst
from heuristic import HeuristicAStar
from state import State
from action import Action
from queue import PriorityQueue
from itertools import count
import copy
import sys


class Root:
    def __init__(self, num_agents, count=0):
        self.count = count
        self.solution = []
        self.cost = 0
        self.idx_constraints = [set() for _ in range(num_agents)]

    def get_conflict(self) -> "bool" or "Conflict":
        longest_plan = len(max(self.solution, key=len))
        state = copy.deepcopy(self.initial_state)
        for step in range(longest_plan):
            joint_action = []
            for agent, _ in enumerate(self.solution):
                try:
                    action = self.solution[agent][step]
                except IndexError:
                    action = [Action.NoOp]
                joint_action = joint_action + action
            # print("JOINT ACTION",joint_action, file = sys.stderr)
            conflicts = state.is_conflict(joint_action, state.t)
            if conflicts:
                return conflicts
            state = state.apply_action(joint_action)
        return False

    def extract_plan(self):
        solution = []
        longest_plan = len(max(self.solution, key=len))
        for step in range(longest_plan):
            joint_action = []
            for agent, _ in enumerate(self.solution):
                try:
                    action = self.solution[agent][step]
                except IndexError:
                    action = [Action.NoOp]
                joint_action = joint_action + action
            solution.append(joint_action)
        return solution


def catch_goal(item, agent, agent_color=None):
    try:
        if int(item) != agent:
            return ""
        return str(0)
    except ValueError:
        return item


def cbs_search(initial_state, frontier):
    root = Root(len(initial_state.agent_rows))
    Root.initial_state = copy.deepcopy(initial_state)
    goals = []
    for agent, _ in enumerate(initial_state.agent_rows):
        state = copy.deepcopy(initial_state)
        sa_frontier = FrontierBestFirst(HeuristicAStar(state))
        agent_row, agent_col = [state.agent_rows[agent]], [state.agent_cols[agent]]
        goal = state._goals
        for row in goal:
            for count, item in enumerate(row):
                row[count] = catch_goal(item, agent)
        sa_state = State(agent_row, agent_col, state.boxes, goal)
        goals.append(goal)
        plan = search(sa_state, sa_frontier)
        root.solution.append(plan)
    frontier.add(root)
    count = 0
    print("ROOT cost", root.cost, file=sys.stderr)
    print("____________________________________", file=sys.stderr)
    while not frontier.is_empty():
        print("COUNT", count, file=sys.stderr)
        if count == 20:
            pass
        node = frontier.pop()
        print("ROOT", node.count, node.solution, file=sys.stderr)
        print("", file=sys.stderr)
        conflicts = node.get_conflict()
        if not conflicts:
            plan = node.extract_plan()
            return plan
        for conflict in conflicts:
            agent, constraints = conflict.agent, conflict.constraints
            print("AGENT", agent, file=sys.stderr)
            print("COOONFLICT", conflict.type, conflict.constraints, file=sys.stderr)
            sa_frontier = FrontierBestFirst(HeuristicAStar(initial_state))
            m = copy.deepcopy(node)
            m.count = count
            m.idx_constraints[agent].update(constraints)
            print("CONSTRAINTS", m.idx_constraints[agent], file=sys.stderr)
            agent_row, agent_col = [initial_state.agent_rows[agent]], [
                initial_state.agent_cols[agent]
            ]
            sa_state = State(agent_row, agent_col, initial_state.boxes, goals[agent])
            if not conflict.is_resolveable():
                plan = None
            else:
                plan = search(
                    sa_state, sa_frontier, constraints=m.idx_constraints[agent]
                )
            print("PLAN", plan, file=sys.stderr)
            m.solution[agent] = plan
            frontier.add(m)
            count = count + 1
    print(m.solution, file=sys.stderr)


class ConflictQueue:
    def __init__(self):
        self.queue = PriorityQueue()
        self.set = set()
        self._counter = count()

    def add(self, conflict):
        t = conflict[-1]
        self.queue.put((t, next(self._counter), conflict))
        self.set.add(conflict)

    def pop(self) -> "State":
        return self.queue.get()[2]

    def is_empty(self) -> "bool":
        return self.queue.empty()

    def size(self) -> "int":
        return self.queue.qsize()

    def contains(self, state: "State") -> "bool":
        return state in self.set

    def get_name(self):
        return "CBS"
