
from app.utils.constantes import LAB_SIZE
from collections import deque
from typing import Tuple


class Maze:
    """Representa el laberinto como una matriz de 0 (libre) / 1 (muro)."""
    def __init__(self, size: int = LAB_SIZE):
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.generate_vertical_walls()

    def generate_vertical_walls(self, spacing: int = 3):
        """Genera muros verticales cada `spacing` columnas con huecos alternos."""
        for idx, col in enumerate(range(2, self.size, spacing)):
            for row in range(self.size):
                self.grid[row][col] = 1
            if idx % 2 == 0:
                self.grid[self.size - 1][col] = 0
            else:
                self.grid[0][col] = 0

    def is_free(self, pos: Tuple[int, int]) -> bool:
        r, c = pos
        return 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == 0
