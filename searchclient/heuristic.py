from abc import ABCMeta, abstractmethod
import sys
import math
import heapq

class Heuristic(metaclass=ABCMeta):
    assigned_boxes = []
    assigned_goals = []
    def __init__(self, initial_state: 'State'):
        # Here's a chance to pre-process the static parts of the level.
        #self.x_goal
        #self.y_goal
        #self.num_agents = len(initial_state.agent_rows)
        #for row in initial_state._g:
        #    for col in row:
        #        for
        self.map = initial_state.pre_processed_map

    def h(self, state) -> 'int':

        agent_row = state.agent_rows
        # print(agent_row,file=sys.stderr)
        agent_col = state.agent_cols

        agent_to_box_h = 0
        box_to_goal_h = 0
        find_agent = None
        find_boxes = {}

        #agent to boxes h if only checking one agent at a time. Checks all boxes not just assigned ones atm
        if len(agent_row) == 1:
            for row_pos, row in enumerate(state.boxes):
                for col_pos, col in enumerate(row):
                    if col != '':
                        find_boxes[col] = (col_pos, row_pos)
                        print(find_boxes,file=sys.stderr)
                        box_pos = (col_pos, row_pos)
                        agent_pos = (agent_col[0],agent_row[0])
                        agent_to_box_h+=self.map[agent_pos][box_pos]
                        # print("loop1",agent_to_box_h,file=sys.stderr)

        elif len(agent_row) > 1:
            print("DSFDASFJASDF",len(agent_row,file=sys.stderr))
            for agent, agent_dic in enumerate(self.assigned_boxes):
                for letter in agent_dic[0]:
                    if len(agent_dic[0][letter]) > 0:
                        find_boxes[col] = (col_pos, row_pos)
                        box_pos = (agent_dic[0][letter][0][1],agent_dic[0][letter][0][0])
                        agent_pos = (col[agent],row[agent])
                        agent_to_box_h+=self.map[agent_pos][box_pos]
                        print("loop2",agent_to_box_h,file=sys.stderr)
        #box to goal len == 1
        elif len(agent_row) == 0:
            return print("wtf",file=sys.stderr)  
                      
        for row, rows in enumerate(state._goals):
            for col, cols in enumerate(rows):
                if cols != '' and "A" <= cols <= "Z":
                    box_pos = find_boxes[cols]
                    goal_pos = (col,row)
                    box_to_goal_h+=self.map[goal_pos][box_pos]
        #agent to goal len == 1
        for row, rows in enumerate(state._goals):
            for col, cols in enumerate(rows):
                if cols != '' and "0" <= cols <= "9":
                    goal_pos = (col,row)
                    print("last loop",find_boxes,file=sys.stderr)
                    agent_pos = find_boxes[find_boxes.keys()[-1]]
                    box_to_goal_h+=self.map[goal_pos][box_pos]
        print(box_to_goal_h,file=sys.stderr)

        # if state.agent_numb is not None:
        #     agent_pos = (col[0],row[0])
        #     letters = self.assigned_boxes[state.agent_numb]
        #     for letter in letters[0]:
        #         if len(letters[0][letter])>0:
        #             box_pos = (letters[0][letter][0][1],letters[0][letter][0][0])
        #             agent_to_box_h+=self.map[agent_pos][box_pos]
        # elif find_agent:
        #     for agent, agent_dic in enumerate(self.assigned_boxes):
        #             for letter in agent_dic[0]:
        #                 if len(agent_dic[0][letter]) > 0:
        #                     box_pos = (agent_dic[0][letter][0][1],agent_dic[0][letter][0][0])
        #                     agent_pos = (col[agent],row[agent])
        #                     agent_to_box_h+=self.map[agent_pos][box_pos]

        
        #box to goal h
                     
        # try:
        #     if len(row) > 1:
        #         for agent, agent_dic in enumerate(self.assigned_boxes):
        #             for letter in agent_dic:
        #                 if len(agent_dic[letter]) > 0:
        #                     box_pos = (agent_dic[letter][0][1],agent_dic[letter][0][0])
        #                     agent_pos = (col[agent],row[agent])
        #                     print("BOX POSITION",box_pos,file=sys.stderr)
        #                     print("AGENT POSITION",agent_pos,file=sys.stderr)
        #                     agent_to_box_h+=self.map[agent_pos][box_pos]
        #                 else:
        #                     continue
        # except:

            

        
        
        # if state.count is None: #Checking initial state
        #     #agent to box distances
        #     for i, rows in enumerate(box_loc):
        #         for j, cols in enumerate(rows):
        #             if cols != '':
        #                 box_color = box_colors[ord(cols)-65]
        #                 box_pos = (j,i)
        #                 box_pos_col[cols] = (j,i)
        #                 # if box_color in agent_color_dic:

        #                 for ind, k in enumerate(agent_colors):
        #                     if k == box_color:
        #                         agent_pos = agent_color_dic[box_color][str(ind)]
        #                         agent_to_box_h+=self.map[agent_pos][box_pos]
        #     #box to goal distances - includes initial agent location to agent goal if needed
        #     for i, rows in enumerate(goals):
        #         for j, cols in enumerate(rows):
        #             if cols != '' and cols in box_pos_col:
        #                 goal_pos = (j,i)
        #                 box_pos = box_pos_col[cols]
        #                 box_to_goal_h+=self.map[goal_pos][box_pos]
        #             elif cols != '':
        #                 goal_pos = (j,i)
        #                 agent_pos = (col[int(cols)],row[int(cols)])
        #                 box_to_goal_h+=self.map[goal_pos][agent_pos]
        # else: #Checking state for one agent at a time
        #     agent_color = agent_colors[state.count]
        #     for i, rows in enumerate(box_loc):
        #         for j, cols in enumerate(rows):
        #             if cols != '':
        #                 box_color = box_colors[ord(cols)-65]
        #                 if agent_color == box_color:
        #                     agent_pos = (col[0],row[0])
        #                     box_pos = (j,i)
        #                     box_pos_col[cols] = (j,i)
        #                     agent_to_box_h+=self.map[agent_pos][box_pos]             
        #     #box to goal distances - includes initial agent location to agent goal if needed
        #     for i, rows in enumerate(goals):
        #         for j, cols in enumerate(rows):
        #             if cols != '' and cols in box_pos_col:
        #                 goal_pos = (j,i)
        #                 box_pos = box_pos_col[cols]
        #                 box_to_goal_h+=self.map[goal_pos][box_pos]
        #             elif cols != '':
        #                 goal_pos = (j,i)
        #                 agent_pos = (col[0],row[0])
        #                 box_to_goal_h+=self.map[goal_pos][agent_pos]

        # # print(agent_to_box_h+box_to_goal_h,file=sys.stderr)
        # return agent_to_box_h+box_to_goal_h
        return 0

    @abstractmethod
    def f(self, state: 'State') -> 'int':
        pass

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError


class HeuristicDijkstra(Heuristic):
    def __init__(self, initial_state: 'State'):
        super().__init__(initial_state)


    def f(self, state: 'State') -> 'int':
        return self.h(state)

    def __repr__(self):
        pass

class Dijkstra():
    def __init__(self, initial_state: 'State') -> None:
        self.state = initial_state
        self.agent_colors = self.state.agent_colors
        self.agent_row = self.state.agent_rows
        self.agent_col = self.state.agent_cols

        self.box_colors = self.state.box_colors
        self.box_locations = self.state.boxes
        self.walls = self.state.walls
        self.agent_to_box_h = 0
        self.box_to_goal_h = 0
        self.g = 0
        self.h = 0
        self.f = self.g+self.h

    def euclidean_distance(self, start: list, end: list) -> int: #Euclidean distance - not used atm
        return math.sqrt(abs(start[0]-end[0])**2+abs(start[1]-end[1])**2)

    def create_valid_squares_dic(self) -> dict:
        valid_squares = {(j,i): float('inf') for i,row in enumerate(self.walls) for j,col in enumerate(row) if col is False}
        return valid_squares

    def adjacency_dict(self, valid_dic: dict) -> dict:
        valid_dic = {key:{} for key in valid_dic}
        for i,j in valid_dic:
            vertex = (i,j)
            up = (i, j+1)
            down = (i, j-1)
            left = (i-1, j)
            right = (i+1, j)

            if up in valid_dic:
                if vertex in valid_dic[up]:
                    if vertex in valid_dic[up]:
                        pass
                else:
                    valid_dic[vertex][up] = 1
                    valid_dic[up][vertex] = 1
            if down in valid_dic:
                if vertex in valid_dic[down]:
                    pass
                else:
                    valid_dic[vertex][down] = 1
                    valid_dic[down][vertex] = 1
            if left in valid_dic:
                if vertex in valid_dic[left]:
                    pass
                else:
                    valid_dic[vertex][left] = 1
                    valid_dic[left][vertex] = 1
            if right in valid_dic:
                if vertex in valid_dic[right]:
                    pass
                else:
                    valid_dic[vertex][right] = 1
                    valid_dic[right][vertex] = 1
        return valid_dic


    def dijkstra(self, start: tuple[int, int], distance: dict) -> dict:
        #start is a tuple containing x,y values, i.e. col,rows.
        graph = self.adjacency_dict(distance)
        dist = distance.copy()
        dist[start] = 0
        queue = [(0, start)]

        while queue:
            current_distance, current_vertex = heapq.heappop(queue)
            if current_distance > dist[current_vertex]:
                continue

            for neighbour, cost in graph[current_vertex].items():
                new_distance = current_distance+cost

                if new_distance < dist[neighbour]:
                    dist[neighbour] = new_distance
                    heapq.heappush(queue, (new_distance, neighbour))
        delete_keys = []
        for i,j in dist.items():
            if isinstance(j, float):
                delete_keys.append(i)
        for i in delete_keys:
            del dist[i]
        return dist

    def distance_matrix(self):
        valid = self.create_valid_squares_dic()
        distance_matrix = {key:self.dijkstra(key, valid) for key in valid}
        return distance_matrix


class HeuristicAStar(Heuristic):
    def __init__(self, initial_state: 'State'):
        super().__init__(initial_state)

    def f(self, state: 'State') -> 'int':
        return 0

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
