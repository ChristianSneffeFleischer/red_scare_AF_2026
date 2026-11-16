### Med hjælp fra Claude, har jeg udbygget denne løsning. I simple termer: fjern alle edges der ikke har eksakt ét rødt endpoint (node)
### Dvs. fjern alle edges med ensfarvede ende-nodes. Tjek i de resterende edges: Kan S gå til T heri?
### Først læses graferne ind med en funktion. Dernæst: Et Queue-setup bruges og popping til at bygge den ovenstående constraint ind i grafen.
## Og for at vurdere om s->t i de resterende 

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