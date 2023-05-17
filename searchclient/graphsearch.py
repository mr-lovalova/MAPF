import memory
import time
import sys

from action import Action
from assigner import Assigner
from preprocessing import Preprocessor
globals().update(Action.__members__)

start_time = time.perf_counter()

def search(initial_state, frontier, constraints=set()):
    iterations = 0

    frontier.add(initial_state)
    explored = set()

    while True:
        iterations += 1

        if frontier.is_empty():
            return None
        state = frontier.pop()

        if state.is_goal_state(constraints):
            plan = state.extract_plan()
            return plan

        explored.add(state)

        for child in state.get_expanded_states(constraints):
            if not frontier.contains(child) and child not in explored:
                frontier.add(child)


def print_search_status(explored, frontier):
    status_template = "#Expanded: {:8,}, #Frontier: {:8,}, #Generated: {:8,}, Time: {:3.3f} s\n[Alloc: {:4.2f} MB, MaxAlloc: {:4.2f} MB]"
    elapsed_time = time.perf_counter() - start_time
    print(
        status_template.format(
            len(explored),
            frontier.size(),
            len(explored) + frontier.size(),
            elapsed_time,
            memory.get_usage(),
            memory.max_usage,
        ),
        file=sys.stderr,
        flush=True,
    )
