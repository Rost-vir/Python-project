import tkinter as tk
from ui import LibraryApp
from db import init_db

root = tk.Tk()

init_db()

app = LibraryApp(root)

root.mainloop()