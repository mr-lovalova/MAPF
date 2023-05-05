from abc import ABCMeta, abstractmethod
import sys

class Heuristic(metaclass=ABCMeta):
    def __init__(self, initial_state: 'State'):
        # Here's a chance to pre-process the static parts of the level.
        #self.x_goal
        #self.y_goal
        #self.num_agents = len(initial_state.agent_rows)
        #for row in initial_state._g:
        #    for col in row:
        #        for
        self.state = initial_state
        pass
    
    def h(self, state: 'State') -> 'int':
        #dy = abs(node.y - goal.y)
        return 0#D * (dx + dy)
    
    @abstractmethod
    def f(self, state: 'State') -> 'int': pass
    
    @abstractmethod
    def __repr__(self): raise NotImplementedError
class HeuristicRegular(Heuristic):
    def __init__(self, initial_state: 'State'):
        super().__init__(initial_state)
    
    def h(self):
        box_state = self.state.boxes
        goal_state = self.state._goals
        box_letters = self.state.box_letters_pos
        goal_letters = self.state.goal_letters_pos
        agent_boxes = self.state.box_colors_with_agents
        agent_num = len(self.state.agent_rows)
        rows = self.state.agent_rows
        cols = self.state.agent_cols

        agent_to_box_h = 0
        box_to_goal_h = 0

        for i in box_letters:
            if i in goal_letters:
                box_to_goal_h+= abs(box_letters[i][0]-goal_letters[i][0])+abs(box_letters[i][1]-goal_letters[i][1])

        for i in agent_boxes:
            if i is None:
                break
            else:
                agent_to_box_h+= abs(rows[i[0].value]-box_letters[i[1]][0])+abs(cols[i[0].value]-box_letters[i[1]][1])
        print(agent_to_box_h,file=sys.stderr)
        # print(self.state.agent_rows,file=sys.stderr)
        # print(self.state.agent_cols,file=sys.stderr)

        return box_to_goal_h+agent_to_box_h
    
    def f(self, state: 'State') -> 'int':
        pass
    
    def __repr__(self):
        pass

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
