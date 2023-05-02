##### notes
if plan is None and frontier.is_empty:
    plan = merge(conflict, initial_state)
    p1 = []
    p2 = []
    for step in enumerate(plan):
        # print("hehe", step, file=sys.stderr)
        p1.append(step[1][0])
        p2.append(step[1][1])
    plans = [p1, p2]
    # print("HERHEHRERHE", plan, file=sys.stderr)
    # print("HERHEHRERHE", plans, file=sys.stderr)
    for count, agent in enumerate(conflict.agents):
        m.solution[agent] = plans[count]
    frontier.add(m)
