from graphsearch import search
from frontier import FrontierBestFirst
from heuristic import HeuristicAStar, HeuristicDijkstra
from state import State
from action import Action
from queue import PriorityQueue
import copy
import sys
from time import sleep


class Root:
    def __init__(self, num_agents, count=0):
        self.count = count
        self.solution = []
        self.cost = 0
        self.constraints = [set() for _ in range(num_agents)]

    def get_conflict(self) -> "Conflict":
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
            conflicts = state.is_conflict(joint_action, state.t)
            if conflicts:
                return conflicts
            state = state.apply_action(joint_action)
        return None

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

def get_goal_char(letter, letters):
    if letter in letters:
        if ord('0') <= ord(letter) <= ord('9'):
            return "0"
        else:
            return letter
    else:
        return ""

def catch_goals(state, agent):
    n_rows, n_cols = len(state._goals), len(state._goals[0])
    agent_color = state.agent_colors[agent]
    letters = [chr(ord("0") + agent)] + [chr(ord('A') + i) for i in range(26) if state.box_colors[i] == agent_color]
    goal = [[get_goal_char(c, letters) for c in row] for row in state._goals]
    print("GOAL", goal, file=sys.stderr)
    return goal


def cbs_search(initial_state, frontier):
    root = Root(len(initial_state.agent_rows))
    Root.initial_state = copy.deepcopy(initial_state)
    goals = []
    for agent, _ in enumerate(initial_state.agent_rows):
        state = copy.deepcopy(initial_state)
        state2 = copy.deepcopy(initial_state)#Copy2 to fit heuristic input
        sa_frontier = FrontierBestFirst(HeuristicDijkstra(state))
        agent_row, agent_col = [state.agent_rows[agent]], [state.agent_cols[agent]]
        goal = catch_goals(state, agent)
        #changing values in initial_state copy rather than make new State object as this loses the dijkstra map
        state2.agent_rows = agent_row
        state2.agent_cols = agent_col
        state2.count = agent #indicates the current agent
        state2._goals = goal
        sa_state = State(agent_row, agent_col, state.boxes, goal)
        goals.append(goal)
        # print(f"Initial plan for agent: {agent}", file=sys.stderr)
        # plan = search(sa_state, sa_frontier)
        plan = search(state2, sa_frontier) #swapped sa_state for state2
        root.solution.append(plan)
    frontier.add(root)
    count = 0
    # print("ROOT cost", root.cost, file=sys.stderr)
    # print("____________________________________", file=sys.stderr)
    while not frontier.is_empty():
        print("Count:", count, file=sys.stderr)
        node = frontier.pop()
        # print("Root: ", node.count, file=sys.stderr)
        for i, solution in enumerate(node.solution):
            print("Popped:", i, solution, file=sys.stderr)
            pass
        conflict = node.get_conflict()
        if not conflict:
            plan = node.extract_plan()
            return plan
        for agent in conflict.agents:
            constraints = conflict.constraints[agent]
            print("New:", agent, conflict.type, constraints, file=sys.stderr)
            sa_frontier = FrontierBestFirst(HeuristicDijkstra(initial_state))
            m = copy.deepcopy(node)
            m.count = count
            m.constraints[agent].update(constraints)
            print("Total:", agent, m.constraints[agent], file=sys.stderr)
            if not conflict.resolveable[agent]:
                plan = None
            else:
                plan = resolve_conflict(
                    agent, m.constraints[agent], initial_state, goals[agent]
                )
                m.solution[agent] = plan
                if plan:
                    print("Fixed:", agent, plan, file=sys.stderr)
                    frontier.add(m)
        count += 1
        print("____________________________________", file=sys.stderr)
    # print(m.solution, file=sys.stderr)


def resolve_conflict(agent, constraints, initial_state, goal):
    sa_frontier = FrontierBestFirst(HeuristicDijkstra(initial_state))
    agent_row, agent_col = [initial_state.agent_rows[agent]], [
        initial_state.agent_cols[agent]
    ]
    sa_state2 = copy.deepcopy(initial_state)
    sa_state2.agent_rows = agent_row
    sa_state2.agent_cols = agent_col
    sa_state2._goals = goal
    sa_state = State(agent_row, agent_col, initial_state.boxes, goal)
    # print(f"Conflict resolution search for agent {agent}", file=sys.stderr)
    plan = search(sa_state2, sa_frontier, constraints=constraints)
    return plan
