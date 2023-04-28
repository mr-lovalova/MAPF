import random
import sys

from action import Action, ActionType

class State:
    _RNG = random.Random(1)

    def __init__(self, agent_rows, agent_cols, boxes, goals):
        '''
        Constructs an initial state.
        Arguments are not copied, and therefore should not be modified after being passed in.

        The lists walls, boxes, and goals are indexed from top-left of the level, row-major order (row, col).
               Col 0  Col 1  Col 2  Col 3
        Row 0: (0,0)  (0,1)  (0,2)  (0,3)  ...
        Row 1: (1,0)  (1,1)  (1,2)  (1,3)  ...
        Row 2: (2,0)  (2,1)  (2,2)  (2,3)  ...
        ...

        For example, State.walls[2] is a list of booleans for the third row.
        State.walls[row][col] is True if there's a wall at (row, col).

        The agent rows, columns, and colors are indexed by the agent number.
        For example, self.agent_rows[0] is the row location of agent '0'.

        Note: The state should be considered immutable after it has been hashed, e.g. added to a dictionary or set.
        '''
        self._goals = goals
        self.agent_rows = agent_rows
        self.agent_cols = agent_cols
        self.boxes = boxes
        self.parent = None
        self.joint_action = None
        self.g = 0
        self._hash = None

    def apply_action(self, joint_action: '[Action, ...]') -> 'State':
        '''
        Returns the state resulting from applying joint_action in this state.
        Precondition: Joint action must be applicable and non-conflicting in this state.
        '''
        # Copy this state.
        copy_agent_rows = self.agent_rows[:]
        copy_agent_cols = self.agent_cols[:]
        copy_boxes = [row[:] for row in self.boxes]

        # Apply each action.
        for agent, action in enumerate(joint_action):
            if action.type is ActionType.NoOp:
                pass

            elif action.type is ActionType.Move:
                copy_agent_rows[agent] += action.agent_row_delta
                copy_agent_cols[agent] += action.agent_col_delta

            elif action.type is ActionType.Push:
                copy_agent_rows[agent] += action.agent_row_delta
                copy_agent_cols[agent] += action.agent_col_delta
                copy_boxes[copy_agent_rows[agent] + action.box_row_delta][copy_agent_cols[agent] + action.box_col_delta] = copy_boxes[copy_agent_rows[agent]][copy_agent_cols[agent]]
                copy_boxes[copy_agent_rows[agent]][copy_agent_cols[agent]] = ""

            elif action.type is ActionType.Pull:
                copy_boxes[copy_agent_rows[agent]][copy_agent_cols[agent]] = copy_boxes[copy_agent_rows[agent] - action.box_row_delta][copy_agent_cols[agent] - action.box_col_delta]
                copy_boxes[copy_agent_rows[agent] - action.box_row_delta][copy_agent_cols[agent] - action.box_col_delta] = ""
                copy_agent_rows[agent] += action.agent_row_delta
                copy_agent_cols[agent] += action.agent_col_delta

        copy_state = State(copy_agent_rows, copy_agent_cols, copy_boxes, self._goals)

        copy_state.parent = self
        copy_state.joint_action = joint_action[:]
        copy_state.g = self.g + 1
        return copy_state

    def is_goal_state(self) -> 'bool':
        for row in range(len(self._goals)):
            for col in range(len(self._goals[row])):
                goal = self._goals[row][col]
                if 'A' <= goal <= 'Z' and self.boxes[row][col] != goal:
                    return False
                elif '0' <= goal <= '9' and not (self.agent_rows[ord(goal) - ord('0')] == row and self.agent_cols[ord(goal) - ord('0')] == col):
                    return False
        return True

    def get_expanded_states(self, constraints) -> '[State, ...]':
        num_agents = len(self.agent_rows)
        # Determine list of applicable action for each individual agent.
        applicable_actions = [[action for action in Action if self.is_applicable(agent, action, constraints)] for agent in range(num_agents)]
        joint_action = [None for _ in range(num_agents)]
        actions_permutation = [0 for _ in range(num_agents)]
        expanded_states = []
        while True:
            for agent in range(num_agents):
                try:
                    joint_action[agent] = applicable_actions[agent][actions_permutation[agent]]
                except IndexError:
                    print(actions_permutation, file = sys.stderr)
                    return expanded_states

            if not self.is_conflicting(joint_action):
                expanded_states.append(self.apply_action(joint_action))

            # Advance permutation.
            done = False
            for agent in range(num_agents):
                if actions_permutation[agent] < len(applicable_actions[agent]) - 1:
                    actions_permutation[agent] += 1
                    break
                else:
                    actions_permutation[agent] = 0
                    if agent == num_agents - 1:
                        done = True

            # Last permutation?
            if done:
                break
        #print((self.agent_rows[0], self.agent_cols[0]),len(expanded_states), file = sys.stderr)
        State._RNG.shuffle(expanded_states)
        return expanded_states

    def is_applicable(self, agent: 'int', action: 'Action', constraints) -> 'bool':
        agent_row = self.agent_rows[agent]
        agent_col = self.agent_cols[agent]
        agent_color = State.agent_colors[agent]
        destination_row = agent_row + action.agent_row_delta
        destination_col = agent_col + action.agent_col_delta

        if ((destination_row,destination_col), self.g) in constraints:
            return False

        if action.type is ActionType.NoOp:
            return True
        
        elif action.type is ActionType.Move:
            return self.is_free(destination_row, destination_col)

        elif action.type is ActionType.Push:
            destination_row = agent_row + action.agent_row_delta
            destination_col = agent_col + action.agent_col_delta
            return (
                self.boxes[destination_row][destination_col] != ""
                and State.box_colors[ord(self.boxes[destination_row][destination_col]) - ord('A')] == agent_color
                and self.is_free(destination_row + action.box_row_delta, destination_col + action.box_col_delta)
            )

        return (
            self.boxes[agent_row - action.box_row_delta][agent_col - action.box_col_delta] != ""
            and State.box_colors[ord(
                self.boxes[agent_row - action.box_row_delta][agent_col - action.box_col_delta]
            ) - ord('A')] == agent_color
            and self.is_free(destination_row, destination_col)
        )

    def is_conflicting(self, joint_action: '[Action, ...]') -> 'bool':
        num_agents = len(self.agent_rows)

        destination_rows = [None for _ in range(num_agents)] # row of new cell to become occupied by action
        destination_cols = [None for _ in range(num_agents)] # column of new cell to become occupied by action
        box_rows = [None for _ in range(num_agents)] # current row of box moved by action
        box_cols = [None for _ in range(num_agents)] # current column of box moved by action

        # Collect cells to be occupied and boxes to be moved.
        for agent in range(num_agents):
            action = joint_action[agent]
            agent_row = self.agent_rows[agent]
            agent_col = self.agent_cols[agent]

            if action.type is ActionType.NoOp:
                pass

            elif action.type is ActionType.Move:
                destination_rows[agent] = agent_row + action.agent_row_delta
                destination_cols[agent] = agent_col + action.agent_col_delta
                box_rows[agent] = agent_row # Distinct dummy value.
                box_cols[agent] = agent_col # Distinct dummy value.

        for a1 in range(num_agents):
            if joint_action[a1] is Action.NoOp:
                continue

            for a2 in range(a1 + 1, num_agents):
                if joint_action[a2] is Action.NoOp:
                    continue

                # Moving into same cell?
                if destination_rows[a1] == destination_rows[a2] and destination_cols[a1] == destination_cols[a2]:
                    return True

        return False

    def is_free(self, row: 'int', col: 'int') -> 'bool':
        return not State.walls[row][col] and self.boxes[row][col] == '' and self.agent_at(row, col) is None
    
    def is_conflict(self, joint_action: '[Action, ...]', time):
        num_agents = len(self.agent_rows)
        directions = ((1,0),(-1,0),(0,1),(0,-1))
        num_agents = len(joint_action)
        blocked_agents = [False for _ in range(num_agents)]
        destination_rows = [None for _ in range(num_agents)] # row of new cell to become occupied by action
        destination_cols = [None for _ in range(num_agents)] # column of new cell to become occupied by action
        box_rows = [None for _ in range(num_agents)] # current row of box moved by action
        box_cols = [None for _ in range(num_agents)] # current column of box moved by action

        # Collect cells to be occupied and boxes to be moved.
        for agent in range(num_agents):
            action = joint_action[agent]
            agent_row = self.agent_rows[agent]
            agent_col = self.agent_cols[agent]
            for direction in directions:
                if self.is_free(agent_row + direction[0],agent_col + direction[1]):
                    break
            else:
                blocked_agents[agent] = True

            if action.type is ActionType.NoOp:
                destination_rows[agent] = agent_row
                destination_cols[agent] = agent_col

            elif action.type is ActionType.Move:
                destination_rows[agent] = agent_row + action.agent_row_delta
                destination_cols[agent] = agent_col + action.agent_col_delta

        for a1 in range(num_agents):
            for a2 in range(a1 + 1, num_agents):
                if destination_rows[a1] == destination_rows[a2] and destination_cols[a1] == destination_cols[a2]:
                    type_ = "VERTEX"
                    constraint = ((destination_rows[a1], destination_cols[a1]),time)
                    c1 = Conflict(a1,blocked_agents[a1], type_)
                    c2 = Conflict(a2,blocked_agents[a2], type_)
                    c1.add_constraint(constraint)
                    c2.add_constraint(constraint)
                    return(c1,c2)
                
                elif (destination_rows[a1] == self.agent_rows[a2] and destination_cols[a1] == self.agent_cols[a2] and
                      destination_rows[a2] == self.agent_rows[a1] and destination_cols[a2] == self.agent_cols[a1]):
                    type_ = "EDGE"
                    c1 = Conflict(a1,blocked_agents[a1], type_)
                    c2 = Conflict(a2,blocked_agents[a2], type_)
                    c1.add_constraint( ((destination_rows[a1], destination_cols[a1]),time))
                    #c1.add_constraint( ((destination_rows[a2], destination_cols[a2]),time - 1))
                    c2.add_constraint( ((destination_rows[a2], destination_cols[a2]), time))
                    #c2.add_constraint( ((destination_rows[a1], destination_cols[a1]), time -1))
                    return(c1, c2)
                
                elif destination_rows[a1] == self.agent_rows[a2] and destination_cols[a1] == self.agent_cols[a2]:
                    type_ = "FOLLOWONE"
                    c1 = Conflict(a1,blocked_agents[a1],type_)
                    c2 = Conflict(a2,blocked_agents[a2], type_)
                    c1.add_constraint(((destination_rows[a1], destination_cols[a1]),time))
                    c2.add_constraint(((destination_rows[a1], destination_cols[a1]),time-1))
                    return(c1, c2)

                elif destination_rows[a2] == self.agent_rows[a1] and destination_cols[a2] == self.agent_cols[a1]:
                    type_ = "FOLLOW"
                    c1 = Conflict(a1,blocked_agents[a1], type_)
                    c2 = Conflict(a2,blocked_agents[a2], type_)
                    c1.add_constraint(((destination_rows[a2], destination_cols[a2]),time-1))
                    c2.add_constraint(((destination_rows[a2], destination_cols[a2]),time))
                    return(c1, c2)

        return False

    def agent_at(self, row: 'int', col: 'int') -> 'char':
        for agent in range(len(self.agent_rows)):
            if self.agent_rows[agent] == row and self.agent_cols[agent] == col:
                return chr(agent + ord('0'))
        return None

    def extract_plan(self) -> '[Action, ...]':
        plan = [None for _ in range(self.g)]
        state = self
        while state.joint_action is not None:
            plan[state.g - 1] = state.joint_action
            state = state.parent
        return plan

    def __hash__(self):
        if self._hash is None:
            prime = 31
            _hash = 1
            _hash = _hash * prime + hash(tuple(self.agent_rows))
            _hash = _hash * prime + hash(tuple(self.agent_cols))
            _hash = _hash * prime + hash(tuple(State.agent_colors))
            _hash = _hash * prime + hash(tuple(tuple(row) for row in self.boxes))
            _hash = _hash * prime + hash(tuple(State.box_colors))
            _hash = _hash * prime + hash(tuple(tuple(row) for row in self._goals))
            _hash = _hash * prime + hash(tuple(tuple(row) for row in State.walls))
            _hash = _hash * prime + hash(self.g)
            self._hash = _hash
        return self._hash

    def __eq__(self, other):
        if self is other: return True
        if not isinstance(other, State): return False
        if self.agent_rows != other.agent_rows: return False
        if self.agent_cols != other.agent_cols: return False
        if State.agent_colors != other.agent_colors: return False
        if State.walls != other.walls: return False
        if self.boxes != other.boxes: return False
        if State.box_colors != other.box_colors: return False
        if self._goals != other._goals: return False
        if self.g != other.g: return False ##### makes MAANDERS05 7 sec faster than with timeState??
        return True

    def __repr__(self):
        lines = []
        for row in range(len(self.boxes)):
            line = []
            for col in range(len(self.boxes[row])):
                if self.boxes[row][col] != '': line.append(self.boxes[row][col])
                elif State.walls[row][col] is not None: line.append('+')
                elif self.agent_at(row, col) is not None: line.append(self.agent_at(row, col))
                else: line.append(' ')
            lines.append(''.join(line))
        return '\n'.join(lines)
    
class Conflict:
    def __init__(self, agent, is_blocked, type_ = None):
        self.agent = agent
        self.is_blocked = is_blocked
        self.constraints = set()
        self.is_past = False
        self.type = type_

    def add_constraint(self, constraint):
        #for constraint in constraints:
        if constraint[-1] == -1:
            self.is_blocked = True
        self.constraints.add(constraint)

    def is_resolveable(self):
        if (self.type == "FOLLOW") and self.is_blocked:
            return False # False
        return True