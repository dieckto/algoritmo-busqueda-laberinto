import tkinter as tk
import time
from collections import deque

LAB_SIZE = 15
CELL_SIZE = 30
VELOCIDAD = 0.05 # segundos por movimiento

inicio = (0, 0)
fin = (14, 14)

# Generar laberinto con muros verticales
laberinto = [[0 for _ in range(LAB_SIZE)] for _ in range(LAB_SIZE)]
for idx, col in enumerate(range(2, LAB_SIZE, 3)):
    for fila in range(LAB_SIZE):
        laberinto[fila][col] = 1 # muro completo
    if idx % 2 == 0:
        laberinto[LAB_SIZE-1][col] = 0 # hueco abajo
    else:
        laberinto[0][col] = 0 # hueco arriba

# Interfaz gráfica
root = tk.Tk()
root.title("Laberinto - Búsqueda en Amplitud y Profundidad")

canvas_laberinto = tk.Canvas(root, width=LAB_SIZE*CELL_SIZE, height=LAB_SIZE*CELL_SIZE, bg="white")
canvas_laberinto.grid(row=0, column=0, padx=5, pady=5)

canvas_visitados = tk.Canvas(root, width=LAB_SIZE*CELL_SIZE, height=LAB_SIZE*CELL_SIZE, bg="white")
canvas_visitados.grid(row=0, column=1, padx=5, pady=5)

# Panel para mostrar la cola/pila
frame_info = tk.Frame(root)
frame_info.grid(row=0, column=2, padx=10, sticky="n")
label_info = tk.Label(frame_info, text="Cola (Amplitud)")
label_info.pack()
text_info = tk.Text(frame_info, width=20, height=30)
text_info.pack()

# Controles
frame_controles = tk.Frame(root)
frame_controles.grid(row=1, column=0, columnspan=3, pady=10)

boton_amplitud = tk.Button(frame_controles, text="Iniciar Amplitud (BFS)", command=lambda: ejecutar("amplitud"))
boton_amplitud.pack(side="left", padx=10)

boton_profundidad = tk.Button(frame_controles, text="Iniciar Profundidad (DFS)", command=lambda: ejecutar("profundidad"))
boton_profundidad.pack(side="left", padx=10)

# Variables globales para controlar el estado
busqueda_activa = False
generador_busqueda = None
algoritmo_actual = None

# Dibujar tablero con coordenadas en los bordes
def dibujar_tablero(canvas, data, inicio, fin):
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
    return canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill=color, outline=color)

def mover_punto(canvas, punto, pos):
    x1, y1 = pos[1]*CELL_SIZE, pos[0]*CELL_SIZE
    x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
    canvas.coords(punto, x1+5, y1+5, x2-5, y2-5)

def actualizar_info(pila_o_cola, tipo):
    text_info.delete(1.0, tk.END)
    label_info.config(text=f"{tipo}")
    for nodo in pila_o_cola:
        text_info.insert(tk.END, f"{nodo}\n")
    text_info.see(tk.END)
    root.update()

# Búsqueda en amplitud (cola)
def amplitud_casilla_por_casilla():
    queue = deque([inicio])
    visitados = set([inicio])
    padres = {inicio: None}

    while queue:
        actual = queue.popleft()
        yield actual, padres, queue
        if actual == fin:
            return

        # Explorar vecinos
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]: # Sin diagonales para laberinto
            nx, ny = actual[0]+dx, actual[1]+dy
            vecino = (nx, ny)
            if (0<=nx<LAB_SIZE and 0<=ny<LAB_SIZE and 
                laberinto[nx][ny]==0 and vecino not in visitados):
                queue.append(vecino)
                visitados.add(vecino)
                padres[vecino] = actual

# Búsqueda en profundidad (pila)
def profundidad_casilla_por_casilla():
    stack = [inicio]
    visitados = set([inicio])
    padres = {inicio: None}

    while stack:
        actual = stack.pop()
        yield actual, padres, stack
        if actual == fin:
            return

        # Explorar vecinos
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]: # Sin diagonales para laberinto
            nx, ny = actual[0]+dx, actual[1]+dy
            vecino = (nx, ny)
            if (0<=nx<LAB_SIZE and 0<=ny<LAB_SIZE and 
                laberinto[nx][ny]==0 and vecino not in visitados):
                stack.append(vecino)
                visitados.add(vecino)
                padres[vecino] = actual
    
# Animación
def ejecutar(algoritmo):
    global busqueda_activa, generador_busqueda, algoritmo_actual
    if busqueda_activa:
        return
    
    busqueda_activa = True
    algoritmo_actual = algoritmo
    
    dibujar_tablero(canvas_laberinto, laberinto, inicio, fin)
    dibujar_tablero(canvas_visitados, [[0]*LAB_SIZE for _ in range(LAB_SIZE)], inicio, fin)
    player = crear_punto(canvas_laberinto, inicio, "blue")

    # Desactivar botones de inicio
    boton_amplitud.config(state="disabled")
    boton_profundidad.config(state="disabled")

    if algoritmo == "amplitud":
        generador_busqueda = amplitud_casilla_por_casilla()
    else:
        generador_busqueda = profundidad_casilla_por_casilla()
    
    animar_busqueda(player, inicio)

def animar_busqueda(player, pos):
    global busqueda_activa, generador_busqueda, algoritmo_actual
    
    try:
        if busqueda_activa:
            pos, padres, estructura = next(generador_busqueda)
            mover_punto(canvas_laberinto, player, pos)
            crear_punto(canvas_visitados, pos, "orange")
            if algoritmo_actual == "amplitud":
                actualizar_info(estructura, "Cola (Amplitud)")
            else:
                actualizar_info(estructura, "Pila (Profundidad)")

            if pos == fin:
                reconstruir_camino(padres)
                busqueda_activa = False
                activar_botones_repetir()
                return

            root.after(int(VELOCIDAD * 1000), lambda: animar_busqueda(player, pos))
    except StopIteration:
        busqueda_activa = False
        activar_botones_repetir()

def reconstruir_camino(padres):
    camino = []
    actual = fin
    while actual is not None:
        camino.append(actual)
        actual = padres.get(actual)
    camino.reverse()
    
    # Dibujar camino final
    for i in range(len(camino) - 1):
        x1, y1 = camino[i][1]*CELL_SIZE + CELL_SIZE/2, camino[i][0]*CELL_SIZE + CELL_SIZE/2
        x2, y2 = camino[i+1][1]*CELL_SIZE + CELL_SIZE/2, camino[i+1][0]*CELL_SIZE + CELL_SIZE/2
        canvas_visitados.create_line(x1, y1, x2, y2, fill="red", width=3)

def activar_botones_repetir():
    global boton_amplitud, boton_profundidad
    boton_amplitud.config(text="Repetir Amplitud (BFS)", command=lambda: repetir("amplitud"))
    boton_profundidad.config(text="Repetir Profundidad (DFS)", command=lambda: repetir("profundidad"))
    boton_amplitud.config(state="normal")
    boton_profundidad.config(state="normal")
    
def repetir(algoritmo):
    global busqueda_activa, generador_busqueda, algoritmo_actual
    if busqueda_activa:
        return
    
    dibujar_tablero(canvas_laberinto, laberinto, inicio, fin)
    dibujar_tablero(canvas_visitados, [[0]*LAB_SIZE for _ in range(LAB_SIZE)], inicio, fin)
    player = crear_punto(canvas_laberinto, inicio, "blue")

    boton_amplitud.config(state="disabled")
    boton_profundidad.config(state="disabled")

    algoritmo_actual = algoritmo
    if algoritmo == "amplitud":
        generador_busqueda = amplitud_casilla_por_casilla()
    else:
        generador_busqueda = profundidad_casilla_por_casilla()
    
    busqueda_activa = True
    animar_busqueda(player, inicio)

# Iniciar la interfaz
dibujar_tablero(canvas_laberinto, laberinto, inicio, fin)
dibujar_tablero(canvas_visitados, [[0]*LAB_SIZE for _ in range(LAB_SIZE)], inicio, fin)
root.mainloop()
