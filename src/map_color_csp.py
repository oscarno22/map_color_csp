"""
Oscar Nolen
ITCS 6150

Project 3: Map Coloring CSP
"""

australia_map = {
    "WA": ["NT", "SA"],
    "NT": ["WA", "SA", "Q"],
    "SA": ["WA", "NT", "Q", "NSW", "V"],
    "Q": ["NT", "SA", "NSW"],
    "NSW": ["Q", "SA", "V"],
    "V": ["SA", "NSW"],
    "TS": []
}


def chromatic_number(mapp):
    colors = 1
    while True:
        coloring = color_dfs(mapp, colors)
        if coloring:
            return colors, coloring
        colors += 1


def can_color(state, color, coloring, mapp):
    for neighbor in mapp[state]:
        if coloring.get(neighbor) == color:
            return False
    return True


def color_dfs(mapp, colors):
    states = list(mapp.keys())
    coloring = {state: 0 for state in states}
    stack = [(states[0], 1)]

    state_index = {state: idx for idx, state in enumerate(states)}

    while stack:
        state, color = stack.pop()

        if can_color(state, color, coloring, mapp):
            coloring[state] = color
            if all(coloring[s] > 0 for s in states):
                return coloring

            next_state_idx = state_index[state] + 1
            if next_state_idx < len(states):
                next_state = states[next_state_idx]
                for next_color in range(1, colors + 1):
                    stack.append((next_state, next_color))
        else:
            coloring[state] = 0

    return None


def main():
    print("hello world")


if __name__ == '__main__':
    main()
