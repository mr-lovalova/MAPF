from abc import ABCMeta, abstractmethod


class Heuristic(metaclass=ABCMeta):
    def __init__(self, initial_state: 'State'):
        pass

    def h(self, state) -> 'int':
        return 0

    @abstractmethod
    def f(self, state: 'State') -> 'int':
        pass

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError


class HeuristicDijkstra:
    assigned_boxes = []
    assigned_goals = []
    pre_processed_map = None
    def __init__(self):
        pass

    def h(self, state) -> 'int':
        agent_row = state.agent_rows
        agent_col = state.agent_cols
        agent_to_box_h = 0
        box_to_goal_h = 0
        find_boxes = {}
        goal_amount = 0
        find_goals = {}
        single_goal = None
        for row, rows in enumerate(state._goals):
            for col, cols in enumerate(rows):
                if cols != '':
                    if cols not in find_goals:
                        find_goals[cols] = (col,row)
                        single_goal = cols
                        goal_pos = (col,row)
                        goal_amount+=1
        if goal_amount == 1:
            return self.single_goal(state,find_goals,single_goal)

        if len(agent_row) == 1:
            for row_pos, row in enumerate(state.boxes):
                for col_pos, col in enumerate(row):
                    if col != '':
                        find_boxes[col] = (col_pos, row_pos)
                        box_pos = (col_pos, row_pos)
                        agent_pos = (agent_col[0],agent_row[0])
                        if box_pos in self.pre_processed_map[agent_pos]:
                            agent_to_box_h+=self.pre_processed_map[agent_pos][box_pos]
                        else:
                            continue


        elif len(agent_row) > 1:
            for agent, agent_dic in enumerate(self.assigned_boxes):
                for letter in agent_dic[0]:
                    if len(agent_dic[0][letter]) > 0:
                        find_boxes[col] = (col_pos, row_pos)
                        box_pos = (agent_dic[0][letter][0][1],agent_dic[0][letter][0][0])
                        agent_pos = (col[agent],row[agent])
                        agent_to_box_h+=self.pre_processed_map[agent_pos][box_pos]

        last_box = None
        for row, rows in enumerate(state._goals):
            for col, cols in enumerate(rows):
                if cols != '' and "A" <= cols <= "Z":
                    box_pos = find_boxes[cols]
                    last_box = find_boxes[cols]
                    goal_pos = (col,row)
                    if box_pos in self.pre_processed_map[goal_pos]:
                        box_to_goal_h+=self.pre_processed_map[goal_pos][box_pos]
                    else:
                        continue

        for row, rows in enumerate(state._goals):
            for col, cols in enumerate(rows):
                if cols != '' and "0" <= cols <= "9":
                    if len(find_boxes) > 0:
                        goal_pos = (col,row)
                        agent_pos = find_boxes[list(find_boxes.keys())[-1]]
                        box_to_goal_h+=self.pre_processed_map[goal_pos][box_pos]
                    else:
                        goal_pos = (col,row)
                        agent_pos = last_box
                        box_to_goal_h+=self.pre_processed_map[goal_pos][agent_pos]
        return box_to_goal_h+agent_to_box_h

    def f(self, state: 'State') -> 'int':
        return state.g+self.h(state)

    def __repr__(self):
        pass

    def mult_goals(self, state, goals):
        agent_row = state.agent_rows
        agent_col = state.agent_cols
        agent_to_box_h = 0
        box_to_goal_h = 0
        for row_pos, row in enumerate(state.boxes):
            for col_pos, col in enumerate(row):
                if col in goals:
                    goal_pos = goals[col]
                    box_pos = (col_pos, row_pos)
                    agent_pos = (agent_col[0],agent_row[0])
                    if box_pos in self.pre_processed_map[agent_pos]:
                        agent_to_box_h+=self.pre_processed_map[agent_pos][box_pos]
                    if box_pos in self.pre_processed_map[goal_pos]:
                        box_to_goal_h+=self.pre_processed_map[box_pos][goal_pos]
                    else:
                        continue
        return agent_to_box_h+box_to_goal_h

    def single_goal(self,state,goal,goal_letter):
        agent_row = state.agent_rows[0]
        agent_col = state.agent_cols[0]
        agent_to_box_h = 0
        box_to_agent_h = 0
        for row_pos, row in enumerate(state.boxes):
            for col_pos, col in enumerate(row):
                if col == goal_letter:
                    box_pos = (col_pos, row_pos)
                    goal_pos = goal[col]
                    agent_pos = (agent_col,agent_row)
                    if box_pos in self.pre_processed_map[goal_pos]:
                        agent_to_box_h+=self.pre_processed_map[goal_pos][box_pos]
                    if box_pos in self.pre_processed_map[agent_pos]:
                        agent_to_box_h+=self.pre_processed_map[agent_pos][box_pos]
                    else:
                        continue
        return agent_to_box_h+box_to_agent_h


class HeuristicAStar(Heuristic):
    def __init__(self, initial_state: 'State'):
        super().__init__(initial_state)

    def f(self, state: 'State') -> 'int':
        return state.g + self.h(state)

    def __repr__(self):
        return 'A* evaluation'


class HeuristicWeightedAStar(Heuristic):
    def __init__(self, initial_state: 'State', w: 'int'):
        super().__init__(initial_state)
        self.w = w

    def f(self, state: 'State') -> 'int':
        return state.g + self.w * self.h(state)

    def __repr__(self):
        return 'WA*({}) evaluation'.format(self.w)


class HeuristicGreedy(Heuristic):
    def __init__(self, initial_state: 'State'):
        super().__init__(initial_state)

    def f(self, state: 'State') -> 'int':
        return self.h(state)

    def __repr__(self):
        return 'greedy evaluation'
