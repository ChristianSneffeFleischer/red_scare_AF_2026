# alternate.py: Red Scare!, problem Alternate (A)
# Author: Christian (chfl@itu.dk)

## !Danish notes whilst creating script:
### Jeg har udbygget denne løsning, som I simple termer: fjern alle edges der ikke har eksakt ét rødt endpoint (node)
### Dvs. fjern alle edges med ensfarvede ende-nodes. Tjek i de resterende edges: Kan S gå til T heri?
### Først læses graferne ind med en funktion parser_function. Dernæst: Et Queue-setup bruges og popping til at bygge den ovenstående constraint ind i grafen.
## Og for at vurdere om s->t i de resterende 

# !English:
# Idea: a path alternates exactly when every edge on it has exactly one red
# endpoint. So I ignore every edge whose two endpoints have the same colour
# and check whether t is still reachable from s using the remaining edges.
#
# Implementation:
#   1. parse_graph reads an instance (same parser as the rest of the group).
#   2. alternate runs a breadth-first search from s. The colour constraint is
#      built into the search: an edge (u, v) is skipped when u and v have the
#      same colour, so the filtered graph never has to be built explicitly.
#   3. main runs this on every instance in a data directory and writes
#      alternate_results.tsv.
#
# Usage: python3 alternate.py <data directory>
# Runs in O(n + m) per instance, on directed and undirected graphs alike.

import os
import sys
import time
from collections import deque

## Same parser as rest of the group
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
            u, v = line.split(" -- ")
            adj[u].append(v)
            adj[v].append(u)
        else:
            u, v = line.split(" -> ")
            adj[u].append(v)

    return adj, red, s, t

def alternate(adj, red, s, t):
    seen = {s}
    queue = deque([s])
    while queue:
        u = queue.popleft()
        if u == t:
            return True
        for v in adj[u]:
            # colour constraint: exactly one endpoint is red
            if (u in red) != (v in red) and v not in seen:
                seen.add(v)
                queue.append(v)
    return False

def main():
    data_dir = sys.argv[1]               # python3 alternate.py data
    rows = []                            # (instance, n, answer, seconds)

    for filename in sorted(os.listdir(data_dir)):
        if not filename.endswith(".txt"):    # <-- skip README.md etc.
            continue
        path = os.path.join(data_dir, filename)
        name = os.path.splitext(filename)[0]
        try:
            adj, red, s, t = parse_graph(path)
            start = time.perf_counter()
            answer = "true" if alternate(adj, red, s, t) else "false"
            seconds = time.perf_counter() - start
            rows.append((name, len(adj), answer, seconds))
        except Exception as e:           # list problem files instead of crashing
            print("FAILED:", filename, e)

    with open("alternate_results.tsv", "w") as out:
        for name, n, answer, seconds in rows:
            out.write(f"{name}\t{n}\t{answer}\n")

    print("\nGraphs with n >= 500 (for the report table):")
    for name, n, answer, seconds in rows:
        if n >= 500:
            print(f"{name}\t{n}\t{answer}")

    slowest = max(rows, key=lambda row: row[3])
    print(f"\nSlowest: {slowest[0]} (n={slowest[1]}) took {slowest[3]:.4f} s")

if __name__ == "__main__":
    main()