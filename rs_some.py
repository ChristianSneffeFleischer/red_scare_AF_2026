from pathlib import Path
import time
import networkx as nx

def parse_graph(path):
    with open(path) as file:
        lines = [line.strip() for line in file if line.strip()]

    n, m, r = map(int, lines[0].split())
    s, t = lines[1].split()

    red = set()
    adj = {}

    for line in lines[2:2+n]:
        name = line.split()[0]
        if line.endswith("*"):
            red.add(name)
        adj[name] = []

    for line in lines[2+n:2+n+m]:
        if " -- " in line:
            u,v = line.split(" -- ")
            adj[u].append(v)
            adj[v].append(u)
        else:
            u,v = line.split(" -> ")
            adj[u].append(v)

    return adj, red, s, t

def find_directed_path_with_red(G, red, s, t, time_limit=300):
    """
    Check whether there exists a simple directed path from s to t
    that includes at least one red node.
    """

    print("This is a directed graph")

    if s not in G or t not in G:
        return False

    red = set(red)
    start_time = time.time()

    # Each state contains:
    # current vertex, current path, whether a red node was found.
    stack = [(s, {s}, s in red)]

    while stack:

        # Check time limit
        if time.time() - start_time > time_limit:
            return "!?"

        current, path, found_red = stack.pop()

        # Found a valid simple path
        if current == t and found_red:
            return True

        # Explore successors
        for neighbor in G.successors(current):

            # Only visit vertices not already in the current path
            if neighbor not in path:

                next_path = path | {neighbor}
                next_found_red = found_red or neighbor in red

                stack.append(
                    (neighbor, next_path, next_found_red)
                )

    return False

def find_path_with_red(adj, red, s, t):

    adj_sets = {u: set(neighbors) for u, neighbors in adj.items()}

    # Help from AI to be able to differentiat between a directed and undirected graph
    is_directed = any(
    u not in adj_sets.get(v, set())
    for u, neighbors in adj_sets.items()
    for v in neighbors)

    if is_directed:
        #G = nx.DiGraph(adj)
        return str("?!")

    G = nx.Graph(adj)

    if s in red or t in red:
        try:
            return str(nx.has_path(G, s, t))
        except nx.NetworkXNoPath:
            return "False"

    for r in red:

        if r not in G:
            continue

        # Split vertices to enforce vertex-disjoint paths
        H = nx.DiGraph()

        for v in G:
            H.add_edge((v, 0), (v, 1),
                       capacity=2 if v == r else 1)

        for u, v in G.edges():
            H.add_edge((u, 1), (v, 0), capacity=1)
            H.add_edge((v, 1), (u, 0), capacity=1)

        H.add_edge((s, 1), "sink", capacity=1)
        H.add_edge((t, 1), "sink", capacity=1)

        value, flow = nx.maximum_flow(
            H, (r, 1), "sink"
        )

        if value < 2:
            continue

        # Extract paths from positive flow
        paths = []

        for _ in range(2):
            path = [(r, 1)]
            current = path[-1]

            while current != "sink":
                nxt = next(
                    (v for v, f in flow[current].items()
                     if f > 0),
                    None
                )

                if nxt is None:
                    break

                flow[current][nxt] -= 1
                path.append(nxt)
                current = nxt

            if current == "sink":
                paths.append(path)

        if len(paths) != 2:
            continue

        paths = [
            [v[0] for v in p
             if isinstance(v, tuple) and v[1] == 0]
            for p in paths
        ]

        paths = [[r] + p for p in paths]

        p_s = next((p for p in paths if p[-1] == s), None)
        p_t = next((p for p in paths if p[-1] == t), None)

        if p_s is None or p_t is None:
            continue

        return "True" #p_s[::-1] + p_t[1:]

    return "False"
