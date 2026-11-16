"""Solve the Red Scare ``Many`` problem on supported graph classes.

For a graph with start vertex ``s``, target vertex ``t``, and a set of red
vertices, Many asks for the largest number of red vertices on a *simple*
``s``-``t`` path.  The problem is NP-hard on general graphs, so this program
only returns a number when an exact polynomial-time method applies:

* directed acyclic graphs (DAGs), using dynamic programming;
* undirected graphs with at most one red vertex, using vertex-disjoint paths;
* undirected graphs whose cycle rank is at most MAX_CYCLE_RANK.

The last algorithm is exponential only in the fixed cycle-rank bound, and is
therefore polynomial on that well-defined graph class.  Unsupported instances
are printed as ``?!``.

Examples:
    python rs_many.py data/G-ex.txt
    python rs_many.py data
    python rs_many.py data --output many_results.txt
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# Keeping this bound fixed is important for the polynomial-time guarantee of
# the bounded-cycle-rank solver.
MAX_CYCLE_RANK = 8
UNSUPPORTED = "?!"


@dataclass(frozen=True)
class Graph:
    names: tuple[str, ...]
    adjacency: tuple[tuple[int, ...], ...]
    edges: tuple[tuple[int, int], ...]
    input_edge_count: int
    red: frozenset[int]
    start: int
    target: int
    directed: bool

    @property
    def n(self) -> int:
        return len(self.names)

    @property
    def m(self) -> int:
        return self.input_edge_count


@dataclass(frozen=True)
class SolveResult:
    value: int | None
    method: str

    @property
    def display_value(self) -> str:
        return UNSUPPORTED if self.value is None else str(self.value)


def parse_graph(path: Path) -> Graph:
    """Parse one graph in the format documented in data/README.md."""
    with open(path, encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    n, m, _ = map(int, lines[0].split())
    start_name, target_name = lines[1].split()

    red_names: set[str] = set()
    adjacency_by_name: dict[str, list[str]] = {}
    names: list[str] = []
    for line in lines[2 : 2 + n]:
        name = line.split()[0]
        names.append(name)
        adjacency_by_name[name] = []
        if line.endswith("*"):
            red_names.add(name)

    edge_lines = lines[2 + n : 2 + n + m]
    directed = any(" -> " in line for line in edge_lines)
    named_edges: list[tuple[str, str]] = []

    for line in edge_lines:
        if " -- " in line:
            first_name, second_name = line.split(" -- ")
        else:
            first_name, second_name = line.split(" -> ")

        #files contain self-loops. A self-loop cannot occur in a simple path so it can be ignored.

        if first_name == second_name:
            continue

        adjacency_by_name[first_name].append(second_name)
        if not directed:
            adjacency_by_name[second_name].append(first_name)
        named_edges.append((first_name, second_name))

    index = {name: vertex for vertex, name in enumerate(names)}
    edges = tuple((index[first], index[second]) for first, second in named_edges)
    adjacency = tuple(
        tuple(index[neighbour] for neighbour in adjacency_by_name[name])
        for name in names
    )
    return Graph(
        names=tuple(names),
        adjacency=adjacency,
        edges=edges,
        input_edge_count=m,
        red=frozenset(index[name] for name in red_names),
        start=index[start_name],
        target=index[target_name],
        directed=directed,
    )


def reachable_vertices(graph: Graph, source: int) -> set[int]: #this is just BFS
    reached = {source}
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for neighbour in graph.adjacency[vertex]:
            if neighbour not in reached:
                reached.add(neighbour)
                queue.append(neighbour)
    return reached


def solve_dag(graph: Graph) -> int | None: #this returns the DAG answer, or None if the directed graph has a cycle
    indegree = [0] * graph.n
    for _, target in graph.edges:
        indegree[target] += 1

    queue = deque(vertex for vertex, degree in enumerate(indegree) if degree == 0) #topological sorting of the indegrees (Kahn's topological-sort algorithm)
    topological_order: list[int] = []
    while queue:
        vertex = queue.popleft()
        topological_order.append(vertex)
        for neighbour in graph.adjacency[vertex]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                queue.append(neighbour)

    if len(topological_order) != graph.n:
        return None

    best: list[int | None] = [None] * graph.n #now this part is dynamic programming
    best[graph.start] = int(graph.start in graph.red)
    for vertex in topological_order:
        if best[vertex] is None:
            continue
        for neighbour in graph.adjacency[vertex]:
            candidate = best[vertex] + int(neighbour in graph.red)
            if best[neighbour] is None or candidate > best[neighbour]:
                best[neighbour] = candidate

    #reachability is checked before this function is called
    assert best[graph.target] is not None
    return best[graph.target]


@dataclass #this is flow network defining
class FlowEdge:
    target: int
    reverse_index: int
    capacity: int


class FlowNetwork:
    """Small integer-capacity max-flow implementation

    The only flow requested by this program has value at most two, so repeated
    breadth-first augmenting paths are both iterative and efficient
    """

    def __init__(self, vertex_count: int) -> None:
        self.adjacency: list[list[FlowEdge]] = [[] for _ in range(vertex_count)]

    def add_edge(self, source: int, target: int, capacity: int) -> None:
        forward = FlowEdge(target, len(self.adjacency[target]), capacity)
        reverse = FlowEdge(source, len(self.adjacency[source]), 0)
        self.adjacency[source].append(forward)
        self.adjacency[target].append(reverse)

    def max_flow(self, source: int, target: int, limit: int | None = None) -> int:
        flow = 0
        while limit is None or flow < limit:
            parent: list[tuple[int, int] | None] = [None] * len(self.adjacency)
            parent[source] = (source, -1)
            queue = deque([source])
            while queue and parent[target] is None:
                vertex = queue.popleft()
                for edge_index, edge in enumerate(self.adjacency[vertex]):
                    if edge.capacity > 0 and parent[edge.target] is None:
                        parent[edge.target] = (vertex, edge_index)
                        queue.append(edge.target)
            if parent[target] is None:
                break

            amount = (limit - flow) if limit is not None else 10**18
            vertex = target
            while vertex != source:
                parent_step = parent[vertex]
                assert parent_step is not None
                previous, edge_index = parent_step
                edge = self.adjacency[previous][edge_index]
                amount = min(amount, edge.capacity)
                vertex = previous

            vertex = target
            while vertex != source:
                parent_step = parent[vertex]
                assert parent_step is not None
                previous, edge_index = parent_step
                edge = self.adjacency[previous][edge_index]
                edge.capacity -= amount
                reverse = self.adjacency[edge.target][edge.reverse_index]
                reverse.capacity += amount
                vertex = previous
            flow += amount

        return flow


def red_vertex_lies_on_undirected_path(graph: Graph, red_vertex: int) -> bool:
    """Test whether a simple s-t path can contain the sole red vertex.

    For a red vertex other than s and t, this is equivalent to the existence
    of two internally vertex-disjoint paths from the red vertex, one ending at
    s and one at t.  Vertex splitting reduces that question to max flow 2.
    """
    if red_vertex in (graph.start, graph.target):
        return True

    def vertex_in(vertex: int) -> int:
        return 2 * vertex

    def vertex_out(vertex: int) -> int:
        return 2 * vertex + 1

    source = 2 * graph.n
    sink = source + 1
    flow_network = FlowNetwork(2 * graph.n + 2)

    for vertex in range(graph.n):
        capacity = 2 if vertex == red_vertex else 1
        flow_network.add_edge(vertex_in(vertex), vertex_out(vertex), capacity)

    for first, second in graph.edges:
        flow_network.add_edge(vertex_out(first), vertex_in(second), 2)
        flow_network.add_edge(vertex_out(second), vertex_in(first), 2)

    flow_network.add_edge(source, vertex_in(red_vertex), 2)
    flow_network.add_edge(vertex_out(graph.start), sink, 1)
    flow_network.add_edge(vertex_out(graph.target), sink, 1)
    return flow_network.max_flow(source, sink, limit=2) == 2


def component_cycle_rank(graph: Graph, component: set[int]) -> int:
    """Return m - n + 1 for one connected component of an undirected graph."""
    degree_sum = sum(len(graph.adjacency[vertex]) for vertex in component)
    edge_count = degree_sum // 2
    return edge_count - len(component) + 1


def solve_bounded_cycle_rank(graph: Graph) -> int:
    """Enumerate simple paths when the undirected cycle rank is fixed/small."""
    visited = {graph.start}
    start_value = int(graph.start in graph.red)
    best = -1

    # Stack entries are (vertex, index of next neighbour, red count).
    # The explicit stack avoids Python's recursion limit on long sparse graphs.
    stack: list[tuple[int, int, int]] = [(graph.start, 0, start_value)]
    while stack:
        vertex, next_index, red_count = stack[-1]

        if vertex == graph.target:
            best = max(best, red_count)
            visited.remove(vertex)
            stack.pop()
            continue

        if next_index == len(graph.adjacency[vertex]):
            visited.remove(vertex)
            stack.pop()
            continue

        neighbour = graph.adjacency[vertex][next_index]
        stack[-1] = (vertex, next_index + 1, red_count)
        if neighbour in visited:
            continue

        visited.add(neighbour)
        stack.append(
            (neighbour, 0, red_count + int(neighbour in graph.red))
        )

    #reachability is checked before this function is called
    assert best >= 0
    return best


def solve_many(graph: Graph) -> SolveResult:
    if graph.start == graph.target:
        return SolveResult(int(graph.start in graph.red), "start-is-target")

    reachable = reachable_vertices(graph, graph.start)
    if graph.target not in reachable:
        return SolveResult(-1, "unreachable")

    if not graph.red:
        return SolveResult(0, "no-red-vertices")

    if graph.directed:
        answer = solve_dag(graph)
        if answer is not None:
            return SolveResult(answer, "dag-dynamic-programming")
        return SolveResult(None, "unsupported-directed-cycle")

    if len(graph.red) == 1:
        red_vertex = next(iter(graph.red))
        answer = int(red_vertex_lies_on_undirected_path(graph, red_vertex))
        return SolveResult(answer, "undirected-one-red-vertex")

    cycle_rank = component_cycle_rank(graph, reachable)
    if cycle_rank <= MAX_CYCLE_RANK:
        answer = solve_bounded_cycle_rank(graph)
        return SolveResult(answer, f"undirected-cycle-rank-{cycle_rank}")

    return SolveResult(None, f"unsupported-cycle-rank-{cycle_rank}")


def graph_paths(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
        return
    if path.is_dir():
        yield from sorted(path.glob("*.txt"), key=lambda item: item.name.lower())
        return
    raise FileNotFoundError(f"input path does not exist: {path}")


def result_rows(paths: Iterable[Path]) -> list[str]:
    rows = ["instance\tn\tm\tr\tmany\tmethod"]
    for path in paths:
        graph = parse_graph(path)
        result = solve_many(graph)
        rows.append(
            "\t".join(
                (
                    path.stem,
                    str(graph.n),
                    str(graph.m),
                    str(len(graph.red)),
                    result.display_value,
                    result.method,
                )
            )
        )
    return rows


def build_argument_parser() -> argparse.ArgumentParser:
    default_data_directory = Path(__file__).resolve().parent / "data"
    parser = argparse.ArgumentParser(
        description="Solve the Red Scare Many problem on supported graph classes."
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=default_data_directory,
        help="an input .txt file or a directory of input files",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write the tab-separated results to this file instead of stdout",
    )
    return parser


def main() -> int:
    arguments = build_argument_parser().parse_args()
    paths = list(graph_paths(arguments.path))
    output = "\n".join(result_rows(paths)) + "\n"
    if arguments.output is None:
        print(output, end="")
    else:
        arguments.output.write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
