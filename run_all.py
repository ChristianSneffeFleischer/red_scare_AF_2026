import os
import sys
import time
from rs_none import parse_graph, solve_none
from alternate import alternate

HEADER = ["instance", "n", "A", "F", "M", "N", "S"]


def main(data_dir, out_path="results.csv"):
    with open(out_path, "w") as out:
        out.write("\t".join(HEADER) + "\n")

        for name in sorted(os.listdir(data_dir)):
            if name.startswith("."):
                continue
            path = os.path.join(data_dir, name)
            if not os.path.isfile(path):
                continue
            try:
                adj, red, s, t = parse_graph(path)
                n = len(adj)
                none_answer = solve_none(adj, red, s, t)
                alternate_answer = alternate(adj, red, s, t)
            except Exception as e:
                print(f"{name}: {e}", file=sys.stderr)
                continue
            row = [name, str(n), str(alternate_answer).lower(), "-", "-", str(none_answer), "-"]
            out.write("\t".join(row) + "\n")


if __name__ == "__main__":
    start = time.perf_counter()
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
    end = time.perf_counter()
    print(f"Elapsed: {end - start:.4f} seconds")