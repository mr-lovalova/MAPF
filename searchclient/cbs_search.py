from graphsearch import search
from frontier import CBSQueue, FrontierBFS, FrontierDFS, FrontierBestFirst
from heuristic import HeuristicAStar, HeuristicWeightedAStar, HeuristicGreedy
from state import State, TimeState
from action import Action
import copy
import sys

class Root:
    def __init__(self, num_agents):
        self.constraints = set()
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
            conflict = state.is_conflict(joint_action, state.g)
            if conflict:
                return conflict
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
    #print("ROOT cost", root.cost, file = sys.stderr)
    #print("____________________________________", file = sys.stderr)
    while not frontier.is_empty():
        #print("COUNT",count, file = sys.stderr)
        count = count + 1
        if count == 200:
            pass
        node = frontier.pop()
        #print("ROOT",node.solution, file = sys.stderr)
        try:
            conflicts, type_ = node.get_conflict()
        except:
            conflicts = node.get_conflict()
        #print("COOONFLICT",conflicts, file = sys.stderr)
        if not conflicts:
            plan = node.extract_plan()
            print(plan, file = sys.stderr)
            return plan
        for conflict in conflicts:
            agent, v, t = conflict
            #print("AGENT", agent, file = sys.stderr)
            state = copy.deepcopy(initial_state)
            sa_frontier = FrontierBestFirst(HeuristicAStar(state))
            m = copy.deepcopy(node)
            m.idx_constraints[agent].add((v,t))
            #print(m.constraints, file = sys.stderr)
            #print(m.idx_constraints, file = sys.stderr)
            agent_row, agent_col = [initial_state.agent_rows[agent]], [initial_state.agent_cols[agent]]
            sa_state = TimeState(agent_row,agent_col,state.boxes, goals[agent])
            #print("AGENT ROW",sa_state.agent_rows, agent_col, file = sys.stderr)
            if t == -1 and type_ == "FOLLOW": ## alot of overhead it seems?..
                plan = None
            else:
                plan = search(sa_state, sa_frontier, constraints= m.idx_constraints[agent])
            m.solution[agent] = plan
            #print("PLAN",plan, file = sys.stderr)
            #print(m.constraints, file = sys.stderr)
            frontier.add(m)
    #print(m.solution, file = sys.stderr)