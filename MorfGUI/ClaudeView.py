import tkinter as tk
from tkinter import ttk
import OldRaceController.RaceController


def create_grid_app(controller, roster):
    #root = tk.Tk()
    def new_file():
        race_controller = OldRaceController(root, roster, "MORF Race", topview = False)
        return 
    def open_file():
        return 
    def save_file():
        return
    def exit():
        quit()
        return
    def add_row():
        return 
    def score_race():
        return
    
    root = tk.Tk()
    
    root.title("MORF 2026 Roster")
    root.cell_labels("800x600")

    # --- Toolbar ---
    toolbar = tk.Frame(root, bg="#2c3e50", pady=6)
    toolbar.pack(fill=tk.X)
    
    menubar = tk.Menu(toolbar)
    # 2. Create the "File" menu and add commands
    file_menu = tk.Menu(menubar, tearoff=0)
    
    file_menu.add_command(label="New", command=new_file)
    file_menu.add_command(label="Open", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_separator() # Adds a horizontal line separator
    file_menu.add_command(label="Exit", command=exit) # Closes the window
    
    edit_menu = tk.Menu(menubar, tearoff=0)
    edit_menu.add_command(label = "add Row", command=add_row)
    edit_menu.add_command(label="Score", command=score_race)
    

    
    # 3. Add the "File" menu to the menu bar
    menubar.add_cascade(label="File", menu=file_menu)
    menubar.add_cascade(label="Edit", menu=edit_menu)
    root.config(menu=menubar)


    # Status bar
    status_var = tk.StringVar(value="Ready")
    status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN,
                          anchor=tk.W, bg="#ecf0f1", fg="#555")
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # --- Main frame with canvas + scrollbars ---
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Scrollbars
    v_scroll = ttk.Scrollbar(main_frame, orient=tk.VERTICAL)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    h_scroll = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL)
    h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    # Canvas
    canvas = tk.Canvas(main_frame, bg="white",
                       yscrollcommand=v_scroll.set,
                       xscrollcommand=h_scroll.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    v_scroll.config(command=canvas.yview)
    h_scroll.config(command=canvas.xview)

    # Frame inside canvas to hold the grid
    grid_frame = tk.Frame(canvas, bg="white")
    canvas_window = canvas.create_window((0, 0), window=grid_frame, anchor="nw")

    # Style
    HEADER_BG = "#2c3e50"
    HEADER_FG = "white"
    ROW_BG1 = "#ffffff"
    ROW_BG2 = "#f0f4f8"
    SEL_BG = "#3498db"
    SEL_FG = "white"
    CELL_W = 100
    CELL_H = 28
    FONT = ("Helvetica", 10)
    HEADER_FONT = ("Helvetica", 10, "bold")

    selected_cell = [None]
    cell_labels = {}
    column_names = ["sailno", "boatname", "boattype", "section", "rating", "owner", "harbor"]
    col_names = ["Sailno", "Boat Name", "Boat Type", "Section", "Rating", "Owner", "Harbor"]
    col_alignment = ["w", "w", "w", "w", "w", "w", "w"]
    col_width = [5, 15, 15, 6, 12, 20, 12]
    num_rows = 10
    num_cols = len(col_names)

    def build_grid():
        # Clear existing grid
        for widget in grid_frame.winfo_children():
            widget.destroy()
        cell_labels.clear()
        selected_cell[0] = None


        # Column headers
        tk.Label(grid_frame, text="#", bg=HEADER_BG, fg=HEADER_FG,
                 font=HEADER_FONT, width=5, relief=tk.FLAT,
                 bd=1, padx=4).grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        for c in range(num_cols):
            name = col_names[c]
            lbl = tk.Label(grid_frame, text=name, bg=HEADER_BG, fg=HEADER_FG,
                           font=HEADER_FONT, width=col_width[c], relief=tk.FLAT, bd=1)
            lbl.grid(row=0, column=c + 1, sticky="nsew", padx=1, pady=1)

        # Data rows
        r = 1
        sailnos = roster.keys()
        for sailno in sailnos:
            boat = roster[sailno]
            row_bg = ROW_BG1 if r % 2 == 0 else ROW_BG2

            # Row number
            tk.Label(grid_frame, text=str(r), bg=HEADER_BG, fg=HEADER_FG,
                     font=HEADER_FONT, width=5, bd=1, relief=tk.FLAT).grid(
                row=r, column=0, sticky="nsew", padx=1, pady=1)

            for c in range(num_cols):
                index = column_names[c]
                value = boat[index]
                lbl = add_field(r, c+1, value, row_bg)
                cell_labels[(r, c)] = (lbl, row_bg)

                def on_click(event, row=r, col=c, bg=row_bg):
                    # Deselect previous
                    if cell_labels[0] and selected_cell[0] in cell_labels:
                        prev_lbl, prev_bg = cell_labels[selected_cell[0]]
                        prev_lbl.config(bg=prev_bg, fg="#333")
                    # Select new
                    selected_cell[0] = (row, col)
                    lbl, _ = cell_labels[(row, col)]
                    lbl.config(bg=SEL_BG, fg=SEL_FG)
                    col_l = chr(65 + col % 26) if col < 26 else chr(65 + col // 26 - 1) + chr(65 + col % 26)
                    status_var.set(f"Selected: {col_l}{row}  |  Row {row}, Column {col + 1}")

                lbl.bind("<Button-1>", on_click)
            r += 1

        # Update scroll region
        grid_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        status_var.set(f"Grid built: {num_rows} rows × {num_cols} cols")
        
    def on_enter_key(event):
        print(event)
        return
    def on_lost_focus(event):
        print(event)
        return
    def on_gain_focus(event):
        print(event)
        return
    def on_up_arrow(event):
        print(event)
        return
    def on_down_arrow(event):
        print(event)
        return 
    
    def add_field(row, col, value, bg):
        entry_field = tk.Entry(grid_frame, width = col_width[col-1],
                               font = FONT, bg=bg, bd=1, relief=tk.FLAT, cursor="hand2")
        entry_field.grid(row=row, column=col, sticky='e')
        entry_field.insert(0, value)

        
        entry_field.bind('<Return>', on_enter_key)
        entry_field.bind("<Tab>", on_enter_key)
        entry_field.bind("<FocusOut>", on_lost_focus)
        entry_field.bind("<FocusIn>", on_gain_focus)
        entry_field.bind("<Up>", on_up_arrow)
        entry_field.bind("<Down>", on_down_arrow)
        return entry_field

    # Mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_shift_mousewheel(event):
        canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind("<MouseWheel>", on_mousewheel)
    canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel)

    # Linux scroll support
    canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    # Keep canvas window same width as canvas
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", on_canvas_configure)

    # Initial build
    build_grid()
