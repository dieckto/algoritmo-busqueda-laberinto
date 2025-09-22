import tkinter as tk
import time
from collections import deque

LAB_SIZE = 15
CELL_SIZE = 30
VELOCIDAD = 0.2 # segundos por movimiento

inicio = (0, 0)
fin = (14, 14)

# Generar laberinto con muros verticales
laberinto = [[0 for _ in range(LAB_SIZE)] for _ in range(LAB_SIZE)]
for idx, col in enumerate(range(2, LAB_SIZE, 3)):
    for fila in range(LAB_SIZE):
        laberinto[fila][col] = 1  # muro completo
    if idx % 2 == 0:
        laberinto[LAB_SIZE-1][col] = 0  # hueco abajo
    else:
        laberinto[0][col] = 0  # hueco arriba

# Interfaz gráfica
root = tk.Tk()
root.title("Laberinto - Búsqueda en Amplitud")

canvas_laberinto = tk.Canvas(root, width=LAB_SIZE*CELL_SIZE, height=LAB_SIZE*CELL_SIZE, bg="white")
canvas_laberinto.grid(row=0, column=0)

canvas_visitados = tk.Canvas(root, width=LAB_SIZE*CELL_SIZE, height=LAB_SIZE*CELL_SIZE, bg="white")
canvas_visitados.grid(row=0, column=1)

# Panel para mostrar la cola
frame_info = tk.Frame(root)
frame_info.grid(row=0, column=2, padx=10)
tk.Label(frame_info, text="Cola (Amplitud)").pack()
text_info = tk.Text(frame_info, width=20, height=30)
text_info.pack()

# Controles
frame_controles = tk.Frame(root)
frame_controles.grid(row=1, column=0, columnspan=3, pady=10)

boton_iniciar = tk.Button(frame_controles, text="Iniciar búsqueda", command=lambda: ejecutar())
boton_iniciar.pack(side="left", padx=10)

# Dibujar tablero con coordenadas en los bordes
def dibujar_tablero(canvas, data):
    canvas.delete("all")
    for i in range(LAB_SIZE):
        for j in range(LAB_SIZE):
            x1, y1 = j*CELL_SIZE, i*CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            color = "black" if data[i][j]==1 else "white"
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

    # Coordenadas en los bordes
    for i in range(LAB_SIZE):
        canvas.create_text(5, i*CELL_SIZE + CELL_SIZE/2, text=str(i), anchor="w", font=("Arial", 7))
    for j in range(LAB_SIZE):
        canvas.create_text(j*CELL_SIZE + CELL_SIZE/2, 5, text=str(j), anchor="n", font=("Arial", 7))

    # inicio y fin
    canvas.create_rectangle(inicio[1]*CELL_SIZE, inicio[0]*CELL_SIZE,
                            inicio[1]*CELL_SIZE+CELL_SIZE, inicio[0]*CELL_SIZE+CELL_SIZE, fill="green")
    canvas.create_rectangle(fin[1]*CELL_SIZE, fin[0]*CELL_SIZE,
                            fin[1]*CELL_SIZE+CELL_SIZE, fin[0]*CELL_SIZE+CELL_SIZE, fill="red")

def crear_punto(canvas, pos, color="blue"):
    x1, y1 = pos[1]*CELL_SIZE, pos[0]*CELL_SIZE
    x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
    return canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill=color)

def mover_punto(canvas, punto, pos):
    x1, y1 = pos[1]*CELL_SIZE, pos[0]*CELL_SIZE
    x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
    canvas.coords(punto, x1+5, y1+5, x2-5, y2-5)

def actualizar_info(cola):
    text_info.delete(1.0, tk.END)
    for nodo in cola:
        text_info.insert(tk.END, f"{nodo}\n")
    text_info.see(tk.END)
    root.update()

# Búsqueda en amplitud (cola)
def amplitud_casilla_por_casilla():
    queue = deque([inicio])
    visitados = set([inicio])
    padres = {inicio: None}

    while queue:
        actualizar_info(queue)
        actual = queue.popleft()
        yield actual, padres
        if actual == fin:
            return
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = actual[0]+dx, actual[1]+dy
            vecino = (nx, ny)
            if 0<=nx<LAB_SIZE and 0<=ny<LAB_SIZE and laberinto[nx][ny]==0 and vecino not in visitados:
                queue.append(vecino)
                visitados.add(vecino)
                padres[vecino] = actual

# Animación
def ejecutar():
    dibujar_tablero(canvas_laberinto, laberinto)
    dibujar_tablero(canvas_visitados, [[0]*LAB_SIZE for _ in range(LAB_SIZE)])
    player = crear_punto(canvas_laberinto, inicio, "blue")

    # Ocultar el botón iniciar mientras corre
    boton_iniciar.config(state="disabled")

    gen = amplitud_casilla_por_casilla()

    try:
        for pos, padres in gen:
            mover_punto(canvas_laberinto, player, pos)
            crear_punto(canvas_visitados, pos, "orange")
            root.update()
            time.sleep(VELOCIDAD)
    except StopIteration:
        pass

    # Al terminar, mostrar botón "Repetir"
    boton_repetir = tk.Button(frame_controles, text="Repetir", command=lambda: repetir(boton_repetir))
    boton_repetir.pack(side="left", padx=10)

def repetir(boton_repetir):
    boton_repetir.destroy()  # quita el botón "Repetir"
    boton_iniciar.config(state="normal")  # habilita otra vez el botón "Iniciar búsqueda"
    ejecutar()

dibujar_tablero(canvas_laberinto, laberinto)
dibujar_tablero(canvas_visitados, [[0]*LAB_SIZE for _ in range(LAB_SIZE)])
root.mainloop()
#...