"""
Periodic table dialog window
"""

import tkinter as tk
from tkinter import ttk
import periodictable as pt
from element_data import (
    get_element_color, 
    get_element_info,
    should_use_white_text,
    PERIODIC_TABLE_LAYOUT,
    LANTHANIDES,
    ACTINIDES
)

class PeriodicTableDialog:
    def __init__(self, parent, callback):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Periodic Table")
        self.dialog.geometry("1200x700")
        self.callback = callback
        
        self.setup_ui()
    
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main periodic table
        for row_idx, row in enumerate(PERIODIC_TABLE_LAYOUT):
            for col_idx, element_symbol in enumerate(row):
                if element_symbol and element_symbol not in ['*', '**']:
                    self.create_element_button(main_frame, element_symbol, row_idx, col_idx)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=8, column=0, columnspan=18, sticky='ew', pady=10
        )
        
        # Add lanthanides
        ttk.Label(main_frame, text="*Lanthanides:", font=('Arial', 10, 'bold')).grid(
            row=9, column=0, columnspan=3, sticky='w'
        )
        for idx, element_symbol in enumerate(LANTHANIDES):
            self.create_element_button(main_frame, element_symbol, 9, idx+3)
        
        # Add actinides
        ttk.Label(main_frame, text="**Actinides:", font=('Arial', 10, 'bold')).grid(
            row=10, column=0, columnspan=3, sticky='w'
        )
        for idx, element_symbol in enumerate(ACTINIDES):
            self.create_element_button(main_frame, element_symbol, 10, idx+3)
    
    def create_element_button(self, parent, element_symbol, row, col):
        try:
            info = get_element_info(element_symbol)
            color = get_element_color(element_symbol)
            text_color = 'white' if should_use_white_text(element_symbol, color) else 'black'
            
            btn = tk.Button(
                parent,
                text=f"{element_symbol}\n{info['number']}",
                width=4, height=2,
                bg=color, fg=text_color,
                relief=tk.RAISED,
                command=lambda e=element_symbol: self.select_element(e)
            )
            btn.grid(row=row, column=col, padx=1, pady=1)
        except:
            pass
    
    def select_element(self, element_symbol):
        self.callback(element_symbol)
        self.dialog.destroy()