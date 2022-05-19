import copy
from functools import reduce
from typing import Dict, TypeVar


_T = TypeVar('_T')
GRAPH = Dict[_T, set[_T]]


def get_unknown_dependencies(graph: GRAPH[_T]) -> set[_T]:
    return reduce(set.union, graph.values(), set()) - set(graph)  # type: ignore


def topological_order(graph: GRAPH[_T]) -> tuple[tuple[set[_T], ...], GRAPH[_T]]:
    """TODO: return `raw_graph` split into cycle and unreachable."""
    _ = get_unknown_dependencies(graph)

    raw_graph = copy.deepcopy(graph)
    for item, dependencies in raw_graph.items():
        dependencies.discard(item)

    resolved = []
    while True:
        if not (ordered := set(item for item, deps in raw_graph.items() if not deps)):
            break

        resolved.append(ordered)

        raw_graph = {
            item: deps - ordered
            for item, deps in raw_graph.items()
            if item not in ordered
        }

    return tuple(resolved), raw_graph
