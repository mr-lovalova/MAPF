from graphsearch import search
from frontier import FrontierBestFirst
from heuristic import HeuristicAStar
from state import State
from action import Action
from queue import PriorityQueue
import copy
import sys


class Root:
    def __init__(self, num_agents, count=0):
        self.count = count
        self.solution = []
        self.cost = 0
        self.constraints = [set() for _ in range(num_agents)]

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


def catch_goal(item, *agents):
    try:
        if int(item) not in agents:
            return ""
        return str(agents.index(int(item)))
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
        if count >= 5000:
            pass
        node = frontier.pop()
        print("ROOT", node.count, node.solution, file=sys.stderr)
        print("", file=sys.stderr)
        conflict = node.get_conflict()
        if not conflict:
            plan = node.extract_plan()
            return plan
        for idx, agent in enumerate(conflict.agents):
            constraints = conflict.constraints[agent]
            sa_frontier = FrontierBestFirst(HeuristicAStar(initial_state))
            m = copy.deepcopy(node)
            m.count = count
            m.constraints[agent].update(constraints)
            plan = resolve_conflict(
                agent, m.constraints[agent], initial_state, goals[agent]
            )
            m.solution[agent] = plan
            if not conflict.resolveable[agent]:
                # manually adding follow constraint for time < 0
                other_agent = conflict.agents[::-1][idx]
                m.constraints[other_agent].update(
                    {(conflict.conflict[2], conflict.conflict[3])}
                )
                plan = resolve_conflict(
                    other_agent,
                    m.constraints[other_agent],
                    initial_state,
                    goals[other_agent],
                )
                m.solution[other_agent] = plan

            frontier.add(m)
        count = count + 1
    print(m.solution, file=sys.stderr)


def resolve_conflict(agent, constraints, initial_state, goal):
    sa_frontier = FrontierBestFirst(HeuristicAStar(initial_state))
    agent_row, agent_col = [initial_state.agent_rows[agent]], [
        initial_state.agent_cols[agent]
    ]
    sa_state = State(agent_row, agent_col, initial_state.boxes, goal)
    plan = search(sa_state, sa_frontier, constraints=constraints)
    return plan


def merge(conflict, initial_state):
    agents = conflict.agents
    state = copy.deepcopy(initial_state)
    frontier = FrontierBestFirst(HeuristicAStar(state))
    agent_rows = []
    agent_cols = []
    # print("AGEBTS", agents, file=sys.stderr)
    for agent in agents:
        # print(state.agent_rows[agent], state.agent_cols[agent], file=sys.stderr)
        agent_rows.append(state.agent_rows[agent])
        agent_cols.append(state.agent_cols[agent])
    goal = state._goals
    for row in goal:
        for count, item in enumerate(row):
            row[count] = catch_goal(item, *agents)
    ma_state = State(agent_rows, agent_cols, state.boxes, goal)
    plan = search(ma_state, frontier)
    print(agent_rows, agent_cols, file=sys.stderr)
    print("PLAn", plan, file=sys.stderr)
    return plan
