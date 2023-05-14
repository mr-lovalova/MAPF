from state import State
import sys

class Preprocessor:
    def __init__(self, initial_state: State) -> None:
        self.state = initial_state

    def boxes_to_walls(self):
        box_colors = set(self.state.box_colors)
        agent_colors = set(self.state.agent_colors)
        unassigned_boxes = box_colors - agent_colors
        unassigned_letters = [chr(ord('A') + i) for i in range(26) if self.state.box_colors[i] in unassigned_boxes]
        print(unassigned_letters, file=sys.stderr, flush=True)
        for letter in unassigned_letters:
            for row in range(len(self.state.boxes)):
                for col in range(len(self.state.boxes[0])):
                    if self.state.boxes[row][col] == letter:
                        self.state.boxes[row][col] = ''
                        self.state.walls[row][col] = True

    def preprocess(self) -> State:
        self.boxes_to_walls()
        return self.state
