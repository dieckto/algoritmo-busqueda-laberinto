from typing import List, Tuple, Dict, Optional
from collections import deque   

def breadth_first_search(grid: List[List[int]],
                         start: Tuple[int,int],
                         goal: Tuple[int,int],
                         allow_diagonal: bool = False):
    """
    Generador de búsqueda en amplitud.
    En cada paso cede (current, parents, queue_snapshot).
    """
    neighbors = [(-1,0),(1,0),(0,-1),(0,1)]
    if allow_diagonal:
        neighbors += [(-1,-1),(-1,1),(1,-1),(1,1)]

    queue = deque([start])
    visited = set([start])
    parents: Dict[Tuple[int,int], Optional[Tuple[int,int]]] = {start: None}

    while queue:
        current = queue.popleft()

        # Explora vecinos y encola
        for dx, dy in neighbors:
            nx, ny = current[0] + dx, current[1] + dy
            vecino = (nx, ny)
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] == 0 and vecino not in visited:
                visited.add(vecino)
                parents[vecino] = current
                queue.append(vecino)

        # Cede el paso para que la UI dibuje este nodo y la cola actual
        yield current, parents, list(queue)

        # Si encontramos goal, podemos detenernos (padres contendrá ruta)
        if current == goal:
            return