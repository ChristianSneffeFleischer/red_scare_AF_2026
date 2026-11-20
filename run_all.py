import os
import sys
import time
from rs_none import parse_graph, solve_none
from alternate import alternate
from rs_few import solve_few
from rs_many import parse_graph as parse_many_graph, solve_many

HEADER = ["instance", "n", "A", "F", "M", "N", "S"]


def main(data_dir, out_path="results.txt"):
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
                few_answer = solve_few(adj, red, s, t)
                many_graph = parse_many_graph(path)
                many_answer = solve_many(many_graph).display_value
            except Exception as e:
                print(f"{name}: {e}", file=sys.stderr)
                continue
            row = [
                name,
                str(n),
                str(alternate_answer).lower(),
                str(few_answer),
                many_answer,
                str(none_answer),
                "-",
            ]
            out.write("\t".join(row) + "\n")


if __name__ == "__main__":
    start = time.perf_counter()
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
    end = time.perf_counter()
    print(f"Elapsed: {end - start:.4f} seconds")
