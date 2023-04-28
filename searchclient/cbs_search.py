from graphsearch import search
from frontier import FrontierBestFirst
from heuristic import HeuristicAStar
from state import State
from action import Action
import copy
import sys

class Root:
    def __init__(self, num_agents):
        self.solution = []
        self.cost = 0
        self.idx_constraints = [set() for _ in range(num_agents)]

    def get_conflict(self) -> 'bool' or 'Conflict':
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
            #print("JOINT ACTION",joint_action, file = sys.stderr)
            conflicts = state.is_conflict(joint_action, state.g)
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


def catch_goal(item, agent):
    try:
        if int(item) != agent:
            return('')
        return str(0)
    except:
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
        sa_state = State(agent_row,agent_col,state.boxes, goal)
        goals.append(goal)
        plan = search(sa_state, sa_frontier)
        root.solution.append(plan)
    frontier.add(root)
    count = 0
    print("ROOT cost", root.cost, file = sys.stderr)
    print("____________________________________", file = sys.stderr)
    while not frontier.is_empty():
        print("COUNT",count, file = sys.stderr)
        count = count + 1
        if count == 105:
            break
        node = frontier.pop()
        print("ROOT",node.solution, file = sys.stderr)
        print("", file = sys.stderr)
        conflicts= node.get_conflict()
        if not conflicts:
            plan = node.extract_plan()
            return plan
        for conflict in conflicts:
            print("AGENT", agent, file = sys.stderr)
            print("COOONFLICT", conflict.type, conflict.constraints, file = sys.stderr)
            agent, constraints = conflict.agent, conflict.constraints
            sa_frontier = FrontierBestFirst(HeuristicAStar(initial_state))
            m = copy.deepcopy(node)
            m.idx_constraints[agent].update(constraints)
            agent_row, agent_col = [initial_state.agent_rows[agent]], [initial_state.agent_cols[agent]]
            sa_state = State(agent_row,agent_col,initial_state.boxes, goals[agent])
            plan = search(sa_state, sa_frontier, constraints= m.idx_constraints[agent])
            print("PLAN", plan, file = sys.stderr)
            m.solution[agent] = plan
            frontier.add(m)
    print(m.solution, file = sys.stderr)