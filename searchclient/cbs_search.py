from graphsearch import search
from frontier import FrontierBestFirst
from heuristic import HeuristicAStar
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
        # print(f"Initial plan for agent: {agent}", file=sys.stderr)
        plan = search(sa_state, sa_frontier)
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
        for idx, agent in enumerate(conflict.agents):
            constraints = conflict.constraints[agent]
            print("New:", agent, conflict.type, constraints, file=sys.stderr)
            sa_frontier = FrontierBestFirst(HeuristicAStar(initial_state))
            m = copy.deepcopy(node)
            m.count = count
            m.constraints[agent].update(constraints)
            print("Total:", agent, m.constraints[agent], file=sys.stderr)
            plan = resolve_conflict(
                agent, m.constraints[agent], initial_state, goals[agent]
            )
            m.solution[agent] = plan
            print("Fixed:", agent, plan, file=sys.stderr)
            if not conflict.resolveable[agent]:
                print("Manually added follow constraint", file=sys.stderr)
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
        count += 1
    print(m.solution, file=sys.stderr)


def resolve_conflict(agent, constraints, initial_state, goal):
    sa_frontier = FrontierBestFirst(HeuristicAStar(initial_state))
    agent_row, agent_col = [initial_state.agent_rows[agent]], [
        initial_state.agent_cols[agent]
    ]
    sa_state = State(agent_row, agent_col, initial_state.boxes, goal)
    # print(f"Conflict resolution search for agent {agent}", file=sys.stderr)
    plan = search(sa_state, sa_frontier, constraints=constraints)
    return plan
