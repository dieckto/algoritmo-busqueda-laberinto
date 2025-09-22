import tkinter as tk
from app.views.mainView import MazeApp  

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()
