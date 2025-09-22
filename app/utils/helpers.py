from typing import List, Tuple, Dict, Optional

def reconstruct_path(parents: Dict[Tuple[int,int], Optional[Tuple[int,int]]],
                     start: Tuple[int,int],
                     goal: Tuple[int,int]) -> List[Tuple[int,int]]:
    path: List[Tuple[int,int]] = []
    node = goal
    while node is not None:
        path.append(node)
        node = parents.get(node)
    path.reverse()
    if path and path[0] == start:
        return path
    return []
