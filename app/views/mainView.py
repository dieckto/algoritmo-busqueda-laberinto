from typing import List, Tuple, Dict, Optional
import tkinter as tk  
from app.utils.constantes import *
from app.utils.maze import Maze
from app.utils.bsf import breadth_first_search
from app.utils.helpers import reconstruct_path  

class MazeApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Laberinto - Búsqueda en Amplitud (refactor)")
        self.maze = Maze(LAB_SIZE)

        # canvases
        self.canvas_lab = tk.Canvas(root, width=LAB_SIZE*CELL_SIZE, height=LAB_SIZE*CELL_SIZE, bg="white")
        self.canvas_lab.grid(row=0, column=0)
        self.canvas_vis = tk.Canvas(root, width=LAB_SIZE*CELL_SIZE, height=LAB_SIZE*CELL_SIZE, bg="white")
        self.canvas_vis.grid(row=0, column=1)

        # panel de cola
        frame_info = tk.Frame(root)
        frame_info.grid(row=0, column=2, padx=10)
        tk.Label(frame_info, text="Cola (Amplitud)").pack()
        self.text_info = tk.Text(frame_info, width=20, height=30)
        self.text_info.pack()

        # controles
        frame_ctrl = tk.Frame(root)
        frame_ctrl.grid(row=1, column=0, columnspan=3, pady=10)
        self.btn_start = tk.Button(frame_ctrl, text="Iniciar búsqueda", command=self.start_search)
        self.btn_start.pack(side="left", padx=10)
        self.btn_reset = tk.Button(frame_ctrl, text="Reset", command=self.reset, state="disabled")
        self.btn_reset.pack(side="left", padx=10)

        # marcar inicio/fin
        self.draw_board(self.canvas_lab, self.maze.grid)
        self.draw_board(self.canvas_vis, [[0]*LAB_SIZE for _ in range(LAB_SIZE)])
        self.player_id = None
        self.visited_ids = {}  # map pos -> rect id

        # generator state
        self._gen = None
        self._running = False

    # ---- dibujo ----
    def draw_board(self, canvas: tk.Canvas, grid: List[List[int]]):
        canvas.delete("all")
        for i in range(LAB_SIZE):
            for j in range(LAB_SIZE):
                x1, y1 = j*CELL_SIZE, i*CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                color = "black" if grid[i][j] == 1 else "white"
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
        # coordenadas (borde)
        for i in range(LAB_SIZE):
            canvas.create_text(5, i*CELL_SIZE + CELL_SIZE/2, text=str(i), anchor="w", font=("Arial", 7))
        for j in range(LAB_SIZE):
            canvas.create_text(j*CELL_SIZE + CELL_SIZE/2, 5, text=str(j), anchor="n", font=("Arial", 7))
        # inicio y fin
        si, sj = INICIO
        fi, fj = FIN
        canvas.create_rectangle(sj*CELL_SIZE, si*CELL_SIZE, sj*CELL_SIZE+CELL_SIZE, si*CELL_SIZE+CELL_SIZE, fill="green")
        canvas.create_rectangle(fj*CELL_SIZE, fi*CELL_SIZE, fj*CELL_SIZE+CELL_SIZE, fi*CELL_SIZE+CELL_SIZE, fill="red")

    def create_player(self, pos: Tuple[int,int], color="blue"):
        x1, y1 = pos[1]*CELL_SIZE, pos[0]*CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        return self.canvas_lab.create_oval(x1+5, y1+5, x2-5, y2-5, fill=color)

    def move_player(self, pos: Tuple[int,int]):
        if self.player_id is None:
            self.player_id = self.create_player(pos)
            return
        x1, y1 = pos[1]*CELL_SIZE, pos[0]*CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        self.canvas_lab.coords(self.player_id, x1+5, y1+5, x2-5, y2-5)

    def mark_visited(self, canvas: tk.Canvas, pos: Tuple[int,int], color="orange"):
        if pos in self.visited_ids:
            return
        x1, y1 = pos[1]*CELL_SIZE, pos[0]*CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        rid = canvas.create_rectangle(x1+1, y1+1, x2-1, y2-1, fill=color, outline="")
        self.visited_ids[pos] = rid

    def draw_path(self, path: List[Tuple[int,int]]):
        for pos in path:
            x1, y1 = pos[1]*CELL_SIZE, pos[0]*CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            self.canvas_lab.create_rectangle(x1+3, y1+3, x2-3, y2-3, fill="yellow", outline="")

    def update_queue_display(self, queue_snapshot: List[Tuple[int,int]]):
        self.text_info.delete(1.0, tk.END)
        for nodo in queue_snapshot:
            self.text_info.insert(tk.END, f"{nodo}\n")
        self.text_info.see(tk.END)

    # ---- control de la búsqueda ----
    def start_search(self):
        if self._running:
            return
        self._running = True
        self.btn_start.config(state="disabled")
        self.btn_reset.config(state="disabled")  # habilitar al finalizar
        # reset canvases
        self.draw_board(self.canvas_lab, self.maze.grid)
        self.draw_board(self.canvas_vis, [[0]*LAB_SIZE for _ in range(LAB_SIZE)])
        self.visited_ids.clear()
        self.player_id = None

        self._gen = breadth_first_search(self.maze.grid, INICIO, FIN, allow_diagonal=True)
        # arrancar loop no bloqueante
        self.root.after(0, self._step)

    def _step(self):
        try:
            current, parents, queue_snapshot = next(self._gen)
        except StopIteration:
            # búsqueda terminada; reconstruir ruta y habilitar botones
            self._running = False
            # si FIN está en parents -> hubo ruta
            # parents puede no existir si generator terminó sin encontrar FIN
            try:
                path = reconstruct_path(parents, INICIO, FIN)
            except Exception:
                path = []
            if path:
                self.draw_path(path)
            self.btn_start.config(state="normal")
            self.btn_reset.config(state="normal")
            return

        # actualizar UI con el paso actual
        self.move_player(current)
        self.mark_visited(self.canvas_vis, current, "orange")
        self.update_queue_display(queue_snapshot)
        # siguiente paso después de VELOCIDAD segundos (no bloqueante)
        self.root.after(int(VELOCIDAD * 1000), self._step)

    def reset(self):
        # reconstruir laberinto (si quisieras generar otro aleatorio aquí)
        self.maze = Maze(LAB_SIZE)
        self.draw_board(self.canvas_lab, self.maze.grid)
        self.draw_board(self.canvas_vis, [[0]*LAB_SIZE for _ in range(LAB_SIZE)])
        self.visited_ids.clear()
        self.player_id = None
        self.text_info.delete(1.0, tk.END)
        self.btn_start.config(state="normal")
        self.btn_reset.config(state="disabled")
        self._running = False
        self._gen = None
