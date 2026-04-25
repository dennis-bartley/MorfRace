import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# 
# the base View class
# it handles common spreadsheet activities and passes off
# others to the respective view class
#
class View(ttk.Frame):
    def __init__(self, controller, root, roster, title, geometry, toplevel = False):
        super().__init__(root)
        self.master = root
        self.controller = controller
        self.roster = roster
        self.toplevel = toplevel
        self.title = title
        self.geometry = geometry
        
    def build_ui(self, col_names, menubar):
        
        self.window = self.master
        # 1. Container frame
        
        if self.toplevel:
            #self.window = tk.Toplevel(self.master)
            self.window = tk.Toplevel(self.master)
        
        self.window.geometry(self.geometry)
        
            
        self.window.title(self.title)
        container = ttk.Frame(self.window)
        # 2. Canvas and Scrollbar
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        # 3. Link them
        canvas.configure(yscrollcommand=scrollbar.set)

        # 4. Content Frame (where your grid goes)
        self.content_frame = ttk.Frame(canvas)

        # 5. Embed Frame in Canvas
        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        # 6. Update scrollregion when content changes
        self.content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Layout Canvas and Scrollbar
        #canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 4. Configure the main window to use the menu bar
        self.window.config(menu=menubar)

        icol = 0
        for col_name in col_names:
            if self.toplevel:
                label = tk.Label(self.window, text=col_name, font=("Helvetica", 10, "bold"))
            else:
                label = tk.Label(self.window, text=col_name, font=("Helvetica", 10, "bold"))
            label.grid(row=0, column=icol, padx=10, pady=5, sticky='w')
            icol += 1


        # Container with scrollbars
        container = ttk.Frame(self)
        #container.pack(fill="both", expand=True)
        


        
    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def getColumnNum(self, columns, colName):
        for col in range(len(columns)):
            if columns[col] == colName:
                return col 
        return None 

        # Get a cell in the grid
    def getValue(self, row, col):
        widget = self.widgets[(row,col)]
        value = widget.get()
        return value
    
    # Set the value of a cell in the grid
    def setValue(self, row, col, value):
        widget = self.widgets[(row, col)]
        widget.delete(0, tk.END)
        widget.insert(0, value)
        
    def addField(self, row, col, value):
        entry_field = tk.Entry(self.window, relief="ridge", width=20)
        entry_field.grid(row=row, column=col, sticky='e')
        entry_field.insert(0, value)
        
        entry_field.bind('<Return>', self.on_enter_key)
        entry_field.bind("<Tab>", self.on_enter_key)
        entry_field.bind("<FocusOut>", self.on_lost_focus)
        entry_field.bind("<FocusIn>", self.on_gain_focus)
        entry_field.bind("<Up>", self.on_up_arrow)
        entry_field.bind("<Down>", self.on_down_arrow)

        self.widgets[(row, col)] = entry_field