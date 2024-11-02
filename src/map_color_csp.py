"""
Oscar Nolen
ITCS 6150

Project 3: Map Coloring CSP
"""

import time
import random
import networkx as nx
import matplotlib.pyplot as plt

australia_map = {
    "WA": ["NT", "SA"],
    "NT": ["WA", "SA", "Q"],
    "SA": ["WA", "NT", "Q", "NSW", "V"],
    "Q": ["NT", "SA", "NSW"],
    "NSW": ["Q", "SA", "V"],
    "V": ["SA", "NSW"],
    "TS": []
}

usa_map = {
    "AK": [],
    "AL": ["MS", "TN", "GA", "FL"],
    "AR": ["MO", "TN", "MS", "LA", "TX", "OK"],
    "AZ": ["CA", "NV", "UT", "CO", "NM"],
    "CA": ["OR", "NV", "AZ"],
    "CO": ["WY", "NE", "KS", "OK", "NM", "AZ", "UT"],
    "CT": ["NY", "MA", "RI"],
    "DC": ["MD", "VA"],
    "DE": ["MD", "PA", "NJ"],
    "FL": ["AL", "GA"],
    "GA": ["FL", "AL", "TN", "NC", "SC"],
    "HI": [],
    "IA": ["MN", "WI", "IL", "MO", "NE", "SD"],
    "ID": ["MT", "WY", "UT", "NV", "OR", "WA"],
    "IL": ["IN", "KY", "MO", "IA", "WI"],
    "IN": ["MI", "OH", "KY", "IL"],
    "KS": ["NE", "MO", "OK", "CO"],
    "KY": ["IN", "OH", "WV", "VA", "TN", "MO", "IL"],
    "LA": ["TX", "AR", "MS"],
    "MA": ["RI", "CT", "NY", "NH", "VT"],
    "MD": ["VA", "WV", "PA", "DC", "DE"],
    "ME": ["NH"],
    "MI": ["WI", "IN", "OH"],
    "MN": ["WI", "IA", "SD", "ND"],
    "MO": ["IA", "IL", "KY", "TN", "AR", "OK", "KS", "NE"],
    "MS": ["LA", "AR", "TN", "AL"],
    "MT": ["ND", "SD", "WY", "ID"],
    "NC": ["VA", "TN", "GA", "SC"],
    "ND": ["MN", "SD", "MT"],
    "NE": ["SD", "IA", "MO", "KS", "CO", "WY"],
    "NH": ["VT", "ME", "MA"],
    "NJ": ["DE", "PA", "NY"],
    "NM": ["AZ", "UT", "CO", "OK", "TX"],
    "NV": ["ID", "UT", "AZ", "CA", "OR"],
    "NY": ["NJ", "PA", "VT", "MA", "CT"],
    "OH": ["PA", "WV", "KY", "IN", "MI"],
    "OK": ["KS", "MO", "AR", "TX", "NM", "CO"],
    "OR": ["CA", "NV", "ID", "WA"],
    "PA": ["NY", "NJ", "DE", "MD", "WV", "OH"],
    "RI": ["CT", "MA"],
    "SC": ["GA", "NC"],
    "SD": ["ND", "MN", "IA", "NE", "WY", "MT"],
    "TN": ["KY", "VA", "NC", "GA", "AL", "MS", "AR", "MO"],
    "TX": ["NM", "OK", "AR", "LA"],
    "UT": ["ID", "WY", "CO", "NM", "AZ", "NV"],
    "VA": ["NC", "TN", "KY", "WV", "MD", "DC"],
    "VT": ["NY", "NH", "MA"],
    "WA": ["ID", "OR"],
    "WI": ["MI", "MN", "IA", "IL"],
    "WV": ["OH", "PA", "MD", "VA", "KY"],
    "WY": ["MT", "SD", "NE", "CO", "UT", "ID"]
}


def visualize_coloring(mapp, coloring):
    g = nx.Graph()
    for state, neighbors in mapp.items():
        g.add_node(state)
        for neighbor in neighbors:
            g.add_edge(state, neighbor)

    colors = [coloring[state] for state in g.nodes]
    plt.figure(figsize=(10, 8))
    nx.draw(g, with_labels=True, node_color=colors, cmap=plt.cm.rainbow, node_size=800)
    plt.show()


def chromatic_number(mapp, search_algo):
    colors = 1
    while True:
        print("Running with num_colors =", colors)
        coloring = search_algo(mapp, colors)
        if coloring:
            return colors, coloring
        colors += 1


def can_color(state, color, coloring, mapp):
    for neighbor in mapp[state]:
        if coloring.get(neighbor) == color:
            return False
    return True


def color_dfs(mapp, colors):
    # states = sorted(mapp.keys(), key=lambda x: len(mapp[x]), reverse=True)
    states = list(mapp.keys())
    random.shuffle(states)
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


def forward_check(state, coloring, mapp, colors):
    """Forward checking: Ensure that uncolored neighbors have valid colors available."""
    for neighbor in mapp[state]:
        if coloring[neighbor] == 0:  # If the neighbor is uncolored
            available_colors = set(range(1, colors + 1)) - {coloring[n] for n in mapp[neighbor] if coloring[n] > 0}
            if not available_colors:  # No colors available for this neighbor
                return False
    return True


def color_dfs_forward(mapp, colors):
    # states = sorted(mapp.keys(), key=lambda x: len(mapp[x]), reverse=True)
    states = list(mapp.keys())
    random.shuffle(states)
    coloring = {state: 0 for state in states}  # Initialize all states as uncolored (0)
    stack = [(states[0], 1)]  # Start with the first state and color 1

    state_index = {state: idx for idx, state in enumerate(states)}

    while stack:
        state, color = stack.pop()
        if can_color(state, color, coloring, mapp):
            coloring[state] = color
            # Perform forward checking
            if forward_check(state, coloring, mapp, colors):
                if all(coloring[s] > 0 for s in states):  # All states are colored
                    return coloring

                next_state_idx = state_index[state] + 1
                if next_state_idx < len(states):
                    next_state = states[next_state_idx]
                    for next_color in range(1, colors + 1):
                        stack.append((next_state, next_color))
        else:
            coloring[state] = 0  # Backtrack
    return None


def propagate(coloring, mapp, colors):
    # Initialize queue with singleton states and their only available color, if any
    queue = [
        (s, (set(range(1, colors + 1)) - {coloring[n] for n in mapp[s] if coloring[n] > 0}).pop())
        for s in coloring if coloring[s] == 0
        and len(set(range(1, colors + 1)) - {coloring[n] for n in mapp[s] if coloring[n] > 0}) == 1
    ]
    assignments_made = []

    while queue:
        state, color = queue.pop(0)
        coloring[state] = color
        assignments_made.append(state)

        for neighbor in mapp[state]:
            if coloring[neighbor] == 0:  # Only check uncolored neighbors
                # Determine available colors for this neighbor
                available_colors = set(range(1, colors + 1)) - {coloring[n] for n in mapp[neighbor] if coloring[n] > 0}

                if not available_colors:
                    # Roll back all assignments if a conflict is found
                    for assigned_state in assignments_made:
                        coloring[assigned_state] = 0
                    return False  # Indicate conflict

                elif len(available_colors) == 1:
                    # Add neighbor to queue if it becomes a singleton
                    queue.append((neighbor, available_colors.pop()))

    return True


def color_dfs_forward_prop(mapp, colors):
    # states = sorted(mapp.keys(), key=lambda x: len(mapp[x]), reverse=True)
    states = list(mapp.keys())
    random.shuffle(states)
    coloring = {state: 0 for state in states}
    stack = [(states[0], 1)]

    state_index = {state: idx for idx, state in enumerate(states)}

    while stack:
        state, color = stack.pop()
        if can_color(state, color, coloring, mapp):
            coloring[state] = color
            if forward_check(state, coloring, mapp, colors) and propagate(coloring, mapp, colors):
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
    start = time.time()
    num_colors, coloring = chromatic_number(usa_map, color_dfs)
    end = time.time()
    print(end - start)
    print("Chromatic Number: ", num_colors)
    print("Coloring: ", coloring)
    print("\n")

    start = time.time()
    num_colors, coloring = chromatic_number(usa_map, color_dfs_forward)
    end = time.time()
    print(end - start)
    print("Chromatic Number: ", num_colors)
    print("Coloring: ", coloring)
    print("\n")

    start = time.time()
    num_colors, coloring = chromatic_number(usa_map, color_dfs_forward_prop)
    end = time.time()
    print(end - start)
    print("Chromatic Number: ", num_colors)
    print("Coloring: ", coloring)
    print("\n")

    visualize_coloring(usa_map, coloring)


if __name__ == '__main__':
    main()
