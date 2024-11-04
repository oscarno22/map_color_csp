"""
Oscar Nolen
ITCS 6150

Project 3: Map Coloring CSP
"""
import time
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

backtrack_dfs = 0
backtrack_dfs_for = 0


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


def is_valid(vertex, coloring, col, mapp, states):
    state = states[vertex]
    for neighbor in mapp[state]:
        neighbor_index = states.index(neighbor)
        if coloring[neighbor_index] == col:
            return False
    return True


def next_dfs(coloring, states, mapp):
    min_domain_size = float('inf')
    max_degree = -1
    next_vertex = -1

    for i in range(len(states)):
        if coloring[i] == 0:
            available_colors = sum(1 for col in range(1, len(states) + 1) if is_valid(i, coloring, col, mapp, states))
            degree = len(mapp[states[i]])

            if (available_colors < min_domain_size) or (available_colors == min_domain_size and degree > max_degree):
                min_domain_size = available_colors
                max_degree = degree
                next_vertex = i

    return next_vertex


def lcv_dfs(vertex, coloring, mapp, states, max_colors):
    color_constraints = []

    for color in range(1, max_colors + 1):
        if is_valid(vertex, coloring, color, mapp, states):
            constraint_count = 0
            state = states[vertex]

            for neighbor in mapp[state]:
                neighbor_index = states.index(neighbor)
                if coloring[neighbor_index] == 0 and is_valid(neighbor_index, coloring, color, mapp, states):
                    constraint_count += 1

            color_constraints.append((color, constraint_count))

    color_constraints.sort(key=lambda x: x[1])  # Sort by constraint count (ascending)
    return [color for color, _ in color_constraints]


def search_dfs(colors, coloring, mapp, states):
    global backtrack_dfs
    vertex = next_dfs(coloring, states, mapp)
    if vertex == -1:
        return True

    for col in lcv_dfs(vertex, coloring, mapp, states, colors):
        if is_valid(vertex, coloring, col, mapp, states):
            coloring[vertex] = col  # Assign color
            if search_dfs(colors, coloring, mapp, states):
                return True
            coloring[vertex] = 0  # Backtrack
            backtrack_dfs += 1

    return False


def color_dfs(mapp):
    global backtrack_dfs
    backtrack_dfs = 0
    states = list(mapp.keys())

    for colors in range(1, len(states) + 1):
        print(f"Trying with {colors} color(s)...")
        coloring = [0] * len(states)
        if search_dfs(colors, coloring, mapp, states):
            solution = {states[i]: coloring[i] for i in range(len(coloring))}
            print(f"The chromatic number is: {colors}")
            print(f"Total number of backtracks: {backtrack_dfs}")
            return colors, solution
    return len(states), {states[i]: i for i in range(1, len(states) + 1)}


def forward_check(vertex, coloring, domains, col, mapp, states):
    state = states[vertex]
    removed_colors = []

    for neighbor in mapp[state]:
        neighbor_index = states.index(neighbor)
        if coloring[neighbor_index] == 0 and col in domains[neighbor_index]:
            domains[neighbor_index].remove(col)
            removed_colors.append((neighbor_index, col))  # Track the removed color
            if not domains[neighbor_index]:
                return False, removed_colors
    return True, removed_colors


def restore_domains(removed_colors, domains):
    for neighbor_index, color in removed_colors:
        domains[neighbor_index].add(color)


def next_dfs_for(domains, coloring, states, mapp):
    min_domain_size = float('inf')
    max_degree = -1
    next_vertex = -1

    for i in range(len(states)):
        if coloring[i] == 0:  # Only consider uncolored vertices
            domain_size = len(domains[i])
            degree = len(mapp[states[i]])

            if (domain_size < min_domain_size) or (domain_size == min_domain_size and degree > max_degree):
                min_domain_size = domain_size
                max_degree = degree
                next_vertex = i
    return next_vertex


def lcv_dfs_for(vertex, domains, mapp, states):
    state = states[vertex]
    color_constraints = []

    for color in domains[vertex]:
        constraint_count = 0
        for neighbor in mapp[state]:
            neighbor_index = states.index(neighbor)
            if color in domains[neighbor_index]:
                constraint_count += 1
        color_constraints.append((color, constraint_count))

    color_constraints.sort(key=lambda x: x[1])
    return [color for color, _ in color_constraints]


def search_dfs_for(colors, coloring, mapp, states, domains):
    global backtrack_dfs_for
    vertex = next_dfs_for(domains, coloring, states, mapp)
    if vertex == -1:  # solution found
        return True

    for col in lcv_dfs_for(vertex, domains, mapp, states):
        if is_valid(vertex, coloring, col, mapp, states):
            coloring[vertex] = col  # Assign color
            success, removed_colors = forward_check(vertex, coloring, domains, col, mapp, states)
            if success:
                if search_dfs_for(colors, coloring, mapp, states, domains):
                    return True
            # Backtrack
            coloring[vertex] = 0
            backtrack_dfs_for += 1
            restore_domains(removed_colors, domains)  # Restore in one place after backtracking

    return False


def color_dfs_for(mapp):
    global backtrack_dfs_for
    backtrack_dfs_for = 0
    states = list(mapp.keys())

    for colors in range(1, len(states) + 1):
        print(f"Trying with {colors} color(s)...")
        coloring = [0] * len(states)
        domains = [{col for col in range(1, colors + 1)} for _ in range(len(states))]
        if search_dfs_for(colors, coloring, mapp, states, domains):
            solution = {states[i]: coloring[i] for i in range(len(coloring))}
            print(f"The chromatic number is: {colors}")
            print(f"Total number of backtracks: {backtrack_dfs_for}")
            return colors, solution
    return len(states), {states[i]: i for i in range(1, len(states) + 1)}


def main():
    start = time.time()
    num_colors, solution = color_dfs_for(usa_map)
    end = time.time()
    print("Total time: ", end - start)
    print(solution)
    print("\n")

    visualize_coloring(usa_map, solution)


if __name__ == '__main__':
    main()
