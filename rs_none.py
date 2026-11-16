import sys
import time
from collections import deque

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


def solve_none(adj, red, s, t):
    if s == t:
        return 0

    dist = {s: 0}
    queue = deque([s])

    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v in dist:
                continue
            if v in red and v != t:
                continue
            dist[v] = dist[u] + 1
            if v == t: 
                return dist[v]
            queue.append(v)
    return -1


def main():
    start = time.perf_counter()
    adj, red, s, t = parse_graph(sys.argv[1])
    print(solve_none(adj, red, s, t))
    end = time.perf_counter()
    print(f"Elapsed: {end - start:.4f} seconds")

if __name__ == "__main__":
    main()