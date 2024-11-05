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

num_backtrack = 0


# GRAPH VISUALIZATION

def visualize_coloring(mapp, coloring):
    g = nx.Graph()
    for state, neighbors in mapp.items():  # build graph from adjacency list
        g.add_node(state)
        for neighbor in neighbors:
            g.add_edge(state, neighbor)

    colors = [coloring[state] for state in g.nodes]  # color states with corresponding colors
    plt.figure(figsize=(10, 8))
    nx.draw(g, with_labels=True, node_color=colors, cmap=plt.cm.rainbow, node_size=800)
    plt.show()


# HELPER FUNCTIONS

def is_valid(vertex, coloring, col, mapp, states):
    state = states[vertex]
    for neighbor in mapp[state]:  # iterate through neighbors
        neighbor_index = states.index(neighbor)
        if coloring[neighbor_index] == col:  # color conflict with neighbor is found
            return False
    return True


def forward_check(vertex, coloring, domains, col, mapp, states):
    state = states[vertex]
    removed_colors = []

    for neighbor in mapp[state]:  # iterate through neighbors
        neighbor_idx = states.index(neighbor)
        if coloring[neighbor_idx] == 0 and col in domains[neighbor_idx]:  # if neighbor is unassigned + color conflict
            domains[neighbor_idx].remove(col)  # remove color from neighbor domain
            removed_colors.append((neighbor_idx, col))  # track the removed color
            if not domains[neighbor_idx]:  # if neighbor domain goes to empty set, return False
                return False, removed_colors
    return True, removed_colors  # if no domains become empty, return True


def restore_domains(removed_colors, domains):
    for neighbor_index, color in removed_colors:
        domains[neighbor_index].add(color)


def propagate(coloring, domains, mapp, states, removed_colors):
    singleton_queue = [i for i, domain in enumerate(domains)
                       if len(domain) == 1 and coloring[i] == 0]  # add all states with a singleton domain

    while singleton_queue:
        singleton_vertex = singleton_queue.pop(0)  # pop vertex with singleton domain
        color = next(iter(domains[singleton_vertex]))  # get the singleton color for the given vertex

        for neighbor in mapp[states[singleton_vertex]]:  # iterate through neighbors of vertex
            neighbor_idx = states.index(neighbor)
            if coloring[neighbor_idx] == 0 and color in domains[neighbor_idx]:  # neighbor unassigned + color conflict
                domains[neighbor_idx].remove(color)  # remove color from neighbor domain
                removed_colors.append((neighbor_idx, color))  # track removed color

                if len(domains[neighbor_idx]) == 1:  # if neighbor domain become singleton, add to queue
                    singleton_queue.append(neighbor_idx)

                if not domains[neighbor_idx]:  # if neighbor domain goes to empty set, return False
                    return False

    return True  # if no domains become empty, return True


def next_1(coloring, states, mapp):
    min_domain_size = float('inf')
    max_degree = -1
    next_vertex = -1

    for i in range(len(states)):
        if coloring[i] == 0:  # if state is unassigned
            available_colors = sum(1 for col in range(1, len(states) + 1)
                                   if is_valid(i, coloring, col, mapp, states))  # get size of domain for given state
            degree = len(mapp[states[i]])

            # find state with minimum domain size and break ties with max degree
            if (available_colors < min_domain_size) or (available_colors == min_domain_size and degree > max_degree):
                min_domain_size = available_colors
                max_degree = degree
                next_vertex = i

    return next_vertex


def next_2(domains, coloring, states, mapp):
    min_domain_size = float('inf')
    max_degree = -1
    next_vertex = -1

    for i in range(len(states)):
        if coloring[i] == 0:  # Only consider uncolored states
            domain_size = len(domains[i])
            degree = len(mapp[states[i]])

            # find state with minimum domain size and break ties with max degree
            if (domain_size < min_domain_size) or (domain_size == min_domain_size and degree > max_degree):
                min_domain_size = domain_size
                max_degree = degree
                next_vertex = i

    return next_vertex


def lcv_1(vertex, coloring, mapp, states, colors):
    color_constraints = []  # track colors and the number of constraint each has

    for color in range(1, colors + 1):  # iterate through all colors
        if is_valid(vertex, coloring, color, mapp, states):  # if assigning color to vertex is valid
            constraint_count = 0
            state = states[vertex]

            for neighbor in mapp[state]:  # iterate through neighbors of vertex
                neighbor_idx = states.index(neighbor)
                if coloring[neighbor_idx] == 0:  # if neighbor is unassigned, then color is still in domain
                    constraint_count += 1

            color_constraints.append((color, constraint_count))

    color_constraints.sort(key=lambda x: x[1])  # sort by constraint count (ascending)
    return [color for color, _ in color_constraints]  # return color ordering


def lcv_2(vertex, domains, mapp, states):
    state = states[vertex]
    color_constraints = []  # track colors and the number of constraints each has

    for color in domains[vertex]:  # iterate through colors in state domain
        constraint_count = 0
        for neighbor in mapp[state]:  # iterate through neighbors of state
            neighbor_index = states.index(neighbor)
            if color in domains[neighbor_index]:  # if neighbor unassigned and color in neighbor domain
                constraint_count += 1
        color_constraints.append((color, constraint_count))

    color_constraints.sort(key=lambda x: x[1])  # sort by constraint count (ascending)
    return [color for color, _ in color_constraints]  # return color ordering


# SEARCH ALGORITHMS

def search_dfs(colors, coloring, vertex, mapp, states):
    global num_backtrack
    if vertex == len(states):  # if all vertices have been assigned, return True
        return True

    for col in range(1, colors + 1):  # iterate through all colors
        if is_valid(vertex, coloring, col, mapp, states):  # if color assignment is valid
            coloring[vertex] = col
            if search_dfs(colors, coloring, vertex + 1, mapp, states):  # recursive call with next vertex to assign
                return True
            coloring[vertex] = 0  # undo assignment if backtrack
            num_backtrack += 1

    return False  # if no solution in this call, return False


def search_dfs_h(colors, coloring, mapp, states):
    global num_backtrack
    vertex = next_1(coloring, states, mapp)  # select next vertex with heuristics
    if vertex == -1:  # if all vertices have been assigned, return True
        return True

    for col in lcv_1(vertex, coloring, mapp, states, colors):  # iterate through all colors by LCV
        if is_valid(vertex, coloring, col, mapp, states):  # if color assignment is valid
            coloring[vertex] = col  # Assign color
            if search_dfs_h(colors, coloring, mapp, states):  # recursive call
                return True
            coloring[vertex] = 0  # undo assignment if backtrack
            num_backtrack += 1

    return False  # if no solution in this call, return False


def search_dfs_for(colors, coloring, vertex, mapp, states, domains):
    global num_backtrack
    if vertex == len(states):  # if all vertices have been assigned, return True
        return True

    for col in domains[vertex].copy():  # iterate over colors in vertex domain
        if is_valid(vertex, coloring, col, mapp, states):  # if color assignment is valid
            coloring[vertex] = col
            success, removed_colors = forward_check(vertex, coloring, domains, col, mapp, states)
            if success:  # if forward check did not indicate backtracking
                if search_dfs_for(colors, coloring, vertex + 1, mapp, states, domains):  # recursive call vertex + 1
                    return True
            coloring[vertex] = 0  # undo assignment if backtrack
            num_backtrack += 1
            restore_domains(removed_colors, domains)  # restore domains to pre-forward check

    return False  # if no solution in this call, return False


def search_dfs_for_h(colors, coloring, mapp, states, domains):
    global num_backtrack
    vertex = next_2(domains, coloring, states, mapp)  # select next vertex with heuristics
    if vertex == -1:  # if all vertices have been assigned, return True
        return True

    for col in lcv_2(vertex, domains, mapp, states):  # iterate through vertex domain with LCV
        if is_valid(vertex, coloring, col, mapp, states):  # if color assignment is valid
            coloring[vertex] = col
            success, removed_colors = forward_check(vertex, coloring, domains, col, mapp, states)
            if success:  # if forward check did not indicate backtracking
                if search_dfs_for_h(colors, coloring, mapp, states, domains):  # recursive call
                    return True
            coloring[vertex] = 0  # undo assignment if backtrack
            num_backtrack += 1
            restore_domains(removed_colors, domains)  # restore domains to pre-forward check

    return False  # if no solution in this call, return False


def search_dfs_for_prop(colors, coloring, vertex, mapp, states, domains):
    global num_backtrack
    if vertex == len(states):  # if all vertices have been assigned, return True
        return True

    for col in domains[vertex].copy():  # iterate over colors in vertex domain
        if is_valid(vertex, coloring, col, mapp, states):
            coloring[vertex] = col
            success, removed_colors = forward_check(vertex, coloring, domains, col, mapp, states)
            if success:  # if forward check did not indicate backtracking
                if propagate(coloring, domains, mapp, states, removed_colors):  # if propagation succeeds
                    if search_dfs_for_prop(colors, coloring, vertex + 1, mapp, states, domains):  # recursive call
                        return True
            coloring[vertex] = 0  # undo assignment if backtrack
            num_backtrack += 1
            restore_domains(removed_colors, domains)  # restore domains to pre-forward check and pre-propagation

    return False  # if no solution in this call, return False


def search_dfs_for_prop_h(colors, coloring, mapp, states, domains):
    global num_backtrack
    vertex = next_2(domains, coloring, states, mapp)  # select next vertex with heuristics
    if vertex == -1:  # if all vertices assigned, return True
        return True

    for col in lcv_2(vertex, domains, mapp, states):  # iterate through vertex domain with LCV
        if is_valid(vertex, coloring, col, mapp, states):  # if color assignment is valid
            coloring[vertex] = col
            success, removed_colors = forward_check(vertex, coloring, domains, col, mapp, states)
            if success:  # if forward check succeeds
                if propagate(coloring, domains, mapp, states, removed_colors):  # if propagation succeeds
                    if search_dfs_for_prop_h(colors, coloring, mapp, states, domains):
                        return True
            coloring[vertex] = 0  # undo assignment if backtrack
            num_backtrack += 1
            restore_domains(removed_colors, domains)  # restore domains to pre-forward check and pre-propagation

    return False  # if no solution in this call, return False


# CHROMATIC COLOR FIND

def color_dfs(mapp):
    global num_backtrack
    num_backtrack = 0
    states = list(mapp.keys())  # convert states into list
    random.shuffle(states)
    # states = sorted(mapp.keys(), key=lambda x: len(mapp[x]), reverse=True)

    for colors in range(1, len(states) + 1):  # iterate through increasing number of colors
        print(f"Trying with {colors} color(s)...")
        coloring = [0] * len(states)  # initialize empty color assignment
        if search_dfs(colors, coloring, 0, mapp, states):  # attempt with given number of colors
            solution = {states[i]: coloring[i] for i in range(len(coloring))}  # convert solution to dictionary
            print(f"The chromatic number is: {colors}")
            print(f"Total number of backtracks: {num_backtrack}")
            return colors, solution  # return number of colors + solution
    return len(states), {states[i]: i for i in range(1, len(states) + 1)}  # trivial solution


def color_dfs_h(mapp):
    global num_backtrack
    num_backtrack = 0
    states = list(mapp.keys())  # convert states to list

    for colors in range(1, len(states) + 1):  # iterate through increasing number of colors
        print(f"Trying with {colors} color(s)...")
        coloring = [0] * len(states)  # initialize empty color assignment
        if search_dfs_h(colors, coloring, mapp, states):  # attempt with given number of colors
            solution = {states[i]: coloring[i] for i in range(len(coloring))}  # convert solution to dictionary
            print(f"The chromatic number is: {colors}")
            print(f"Total number of backtracks: {num_backtrack}")
            return colors, solution
    return len(states), {states[i]: i for i in range(1, len(states) + 1)}


def color_dfs_for(mapp):
    global num_backtrack
    num_backtrack = 0
    states = list(mapp.keys())  # convert states to list
    random.shuffle(states)
    states = sorted(mapp.keys(), key=lambda x: len(mapp[x]), reverse=True)

    for colors in range(1, len(states) + 1):  # iterate through increasing number of colors
        print(f"Trying with {colors} color(s)...")
        coloring = [0] * len(states)  # initialize empty color assignment
        domains = [{col for col in range(1, colors + 1)} for _ in range(len(states))]  # initialize domains
        if search_dfs_for(colors, coloring, 0, mapp, states, domains):  # attempt with given number of colors
            solution = {states[i]: coloring[i] for i in range(len(coloring))}
            print(f"The chromatic number is: {colors}")
            print(f"Total number of backtracks: {num_backtrack}")
            return colors, solution
    return len(states), {states[i]: i for i in range(1, len(states) + 1)}


def color_dfs_for_h(mapp):
    global num_backtrack
    num_backtrack = 0
    states = list(mapp.keys())  # convert states to list

    for colors in range(1, len(states) + 1):  # iterate through increasing number of colors
        print(f"Trying with {colors} color(s)...")
        coloring = [0] * len(states)  # initialize empty color assignment
        domains = [{col for col in range(1, colors + 1)} for _ in range(len(states))]  # initialize domains
        if search_dfs_for_h(colors, coloring, mapp, states, domains):  # attempt with given number of colors
            solution = {states[i]: coloring[i] for i in range(len(coloring))}
            print(f"The chromatic number is: {colors}")
            print(f"Total number of backtracks: {num_backtrack}")
            return colors, solution
    return len(states), {states[i]: i for i in range(1, len(states) + 1)}


def color_dfs_for_prop(mapp):
    global num_backtrack
    num_backtrack = 0
    states = list(mapp.keys())  # convert states to list
    random.shuffle(states)
    states = sorted(mapp.keys(), key=lambda x: len(mapp[x]), reverse=True)

    for colors in range(1, len(states) + 1):  # iterate through increasing number of colors
        print(f"Trying with {colors} color(s)...")
        coloring = [0] * len(states)  # initialize empty color assignment
        domains = [{col for col in range(1, colors + 1)} for _ in range(len(states))]  # initialize domains
        if search_dfs_for_prop(colors, coloring, 0, mapp, states, domains):  # attempt with given num of colors
            solution = {states[i]: coloring[i] for i in range(len(coloring))}
            print(f"The chromatic number is: {colors}")
            print(f"Total number of backtracks: {num_backtrack}")
            return colors, solution
    return len(states), {states[i]: i for i in range(1, len(states) + 1)}


def color_dfs_for_prop_h(mapp):
    global num_backtrack
    num_backtrack = 0
    states = list(mapp.keys())  # convert states to list

    for colors in range(1, len(states) + 1):  # iterate through increasing number of colors
        print(f"Trying with {colors} color(s)...")
        coloring = [0] * len(states)  # initialize empty color assignment
        domains = [{col for col in range(1, colors + 1)} for _ in range(len(states))]  # initialize domains
        if search_dfs_for_prop_h(colors, coloring, mapp, states, domains):  # attempt with given number of colors
            solution = {states[i]: coloring[i] for i in range(len(coloring))}
            print(f"The chromatic number is: {colors}")
            print(f"Total number of backtracks: {num_backtrack}")
            return colors, solution
    return len(states), {states[i]: i for i in range(1, len(states) + 1)}


def main():
    start = time.time()
    num_colors, solution = color_dfs(usa_map)
    end = time.time()
    print("Total time: ", end - start)
    print(solution)
    print("\n")

    visualize_coloring(usa_map, solution)


if __name__ == '__main__':
    main()
