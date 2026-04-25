import tkinter as tk
from tkinter import ttk
from Style import *


class GuiView():
    def __init__(self, controller, title, geometry):
        self.controller = controller
        self.geometry = geometry
        self.title = title
        self.root = tk.Tk()

    
    def build_ui(self, col_names, menubar):
        # Status bar
        root = self.root
        root.geometry(self.geometry)
        root.title(self.title)
        root.config(menu=menubar)
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN,
                              anchor=tk.W, bg="#ecf0f1", fg="#555")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
        # --- Main frame with canvas + scrollbars ---
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Scrollbars
        v_scroll = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
        h_scroll = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    
        # Canvas
        canvas = tk.Canvas(self.main_frame, bg="white",
                           yscrollcommand=v_scroll.set,
                           xscrollcommand=h_scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = canvas
    
        v_scroll.config(command=canvas.yview)
        h_scroll.config(command=canvas.xview)
    
        # Frame inside canvas to hold the grid
        self.grid_frame = tk.Frame(canvas, bg="white")
        self.canvas_window = canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
    

        num_rows = 10
        num_cols = len(col_names)
        
    # Get a cell in the grid
    def getValue(self, row, col):
        (widget,bg) = self.widgets[(row,col)]
        value = widget.get()
        return value
    
    # Set the value of a cell in the grid
    def setValue(self, row, col, value):
        (widget, bg) = self.widgets[(row, col)]
        widget.delete(0, tk.END)
        widget.insert(0, value)

        
    