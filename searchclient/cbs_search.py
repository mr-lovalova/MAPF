import copy
import sys

from graphsearch import search
from frontier import FrontierBestFirst, CBSQueue
from heuristic import HeuristicAStar
from state import State
from action import Action
from conflict import Conflict
from preprocessing import Preprocessor
from assigner import Assigner


class Root:
    initial_state = None

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


def catch_items(state, agent):
    def get_goal_char(letter, letters):
        if letter in letters:
            if ord('0') <= ord(letter) <= ord('9'):
                return "0"
            else:
                return letter
        else:
            return ""

    agent_color = state.agent_colors[agent]
    letters = [chr(ord("0") + agent)] + [chr(ord('A') + i) for i in range(26) if state.box_colors[i] == agent_color]
    boxes = [[c if c in letters else "" for c in row] for row in state.boxes]
    goal = [[get_goal_char(c, letters) for c in row] for row in state._goals]
    return boxes, goal

def replace_colors(state: State) -> State:
    """
    Replaces all agents and box colors with that of the first color. This only works when the first agent is agent 0 and it has box A.
    """
    first_box_color = state.box_colors[0]
    for i in range(len(state.box_colors)):
        if state.box_colors[i] is not None:
            state.box_colors[i] = first_box_color

    first_agent_color = state.agent_colors[0]
    for i in range(len(state.agent_colors)):
        if state.agent_colors[i] is not None:
            state.agent_colors[i] = first_agent_color

    return state

def cbs_search(initial_state, frontier):
    root = Root(len(initial_state.agent_rows))
    Root.initial_state = copy.deepcopy(initial_state)
    goals = []
    boxes = []
    for agent, _ in enumerate(initial_state.agent_rows):
        state = copy.deepcopy(initial_state)
        sa_frontier = FrontierBestFirst(HeuristicAStar(state))
        agent_row, agent_col = [state.agent_rows[agent]], [state.agent_cols[agent]]
        box, goal = catch_items(state, agent)
        sa_state = replace_colors(State(agent_row, agent_col, box, goal))
        # print("Boxes:", agent, sa_state.boxes, file=sys.stderr)
        # print("Goals:", agent, sa_state._goals, file=sys.stderr)
        goals.append(goal); boxes.append(box)
        print(f"Initial search for agent {agent}", file=sys.stderr)
        plan = search(sa_state, sa_frontier)
        print(f"Initial plan for agent {agent}: {plan}", file=sys.stderr)
        root.solution.append(plan)
    frontier.add(root)
    count = 0
    while not frontier.is_empty():
        # print("Count:", count, file=sys.stderr)
        node = frontier.pop()
        # for i, solution in enumerate(node.solution):
            # print("Popped:", i, solution, file=sys.stderr)
        conflict = node.get_conflict()
        if conflict is None:
            plan = node.extract_plan()
            return plan
        for agent in conflict.agents:
            constraints = conflict.constraints[agent]
            # print("New:", agent, conflict.type, constraints, file=sys.stderr)
            sa_frontier = FrontierBestFirst(HeuristicAStar(initial_state))
            m = copy.deepcopy(node)
            m.count = count
            m.constraints[agent].update(constraints)
            # print("Total:", agent, m.constraints[agent], file=sys.stderr)
            if not conflict.resolveable[agent]:
                plan = None
            else:
                plan = resolve_conflict(
                    agent, m.constraints[agent], initial_state, boxes[agent], goals[agent]
                )
                m.solution[agent] = plan
                if plan:
                    # print("Fixed:", agent, plan, file=sys.stderr)
                    frontier.add(m)
        count += 1
        # print("____________________________________", file=sys.stderr)


def resolve_conflict(agent, constraints, initial_state, box, goal):
    sa_frontier = FrontierBestFirst(HeuristicAStar(initial_state))
    agent_row, agent_col = [initial_state.agent_rows[agent]], [
        initial_state.agent_cols[agent]
    ]
    sa_state = State(agent_row, agent_col, box, goal)
    # print(f"Conflict resolution search for agent {agent}", file=sys.stderr)
    plan = search(sa_state, sa_frontier, constraints=constraints)
    return plan


def get_final_state(initial_state, plan):
    state = copy.deepcopy(initial_state)
    for joint_action in plan:
        state = state.apply_action(joint_action)
    return state


def sequential_cbs(initial_state):
    state = Preprocessor(initial_state).preprocess()
    assigner = Assigner(state)
    print(assigner.assign_plans(), file=sys.stderr)
    plann = cbs_search(state, CBSQueue())
    print(get_final_state(state, plann), file=sys.stderr)
    return plann
