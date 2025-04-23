#!/usr/bin/env python3
"""
Component Dialog Module for QuickTARA GUI
Provides dialog for adding and editing components
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Set, Optional, List, Callable

class ComponentDialog(tk.Toplevel):
    """Dialog for adding or editing a component"""
    def __init__(self, parent, on_save: Callable, edit_mode: bool = False, 
                 existing_data: Optional[Dict] = None):
        super().__init__(parent)
        self.parent = parent
        self.on_save = on_save
        self.edit_mode = edit_mode
        
        # Configure window
        title = "Edit Component" if edit_mode else "Add Component"
        self.title(title)
        self.geometry("600x650")
        self.resizable(False, False)
        self.grab_set()  # Make dialog modal
        
        # Initialize with existing data if in edit mode
        self.existing_data = existing_data or {}
        
        # Create and layout widgets
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        """Center the dialog on the parent window"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.parent.winfo_width() // 2) - (width // 2) + self.parent.winfo_x()
        y = (self.parent.winfo_height() // 2) - (height // 2) + self.parent.winfo_y()
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create all dialog widgets"""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a scrollable canvas
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create form fields
        self.create_form_fields(scrollable_frame)
        
        # Button frame at the bottom
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Save and Cancel buttons
        save_text = "Update" if self.edit_mode else "Add"
        ttk.Button(button_frame, text=save_text, command=self.save_component).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def create_form_fields(self, parent):
        """Create all form fields"""
        # Basic information section
        ttk.Label(parent, text="Basic Information", font=("TkDefaultFont", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Component ID
        ttk.Label(parent, text="Component ID:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.component_id_var = tk.StringVar(value=self.existing_data.get('component_id', ''))
        ttk.Entry(parent, textvariable=self.component_id_var, width=30).grid(
            row=1, column=1, sticky=tk.W, pady=2)
        
        # Component Name
        ttk.Label(parent, text="Name:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar(value=self.existing_data.get('name', ''))
        ttk.Entry(parent, textvariable=self.name_var, width=30).grid(
            row=2, column=1, sticky=tk.W, pady=2)
        
        # Component Type
        ttk.Label(parent, text="Type:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.type_var = tk.StringVar(value=self.existing_data.get('type', 'ECU'))
        type_options = ['ECU', 'Sensor', 'Gateway', 'Actuator', 'Network']
        ttk.Combobox(parent, textvariable=self.type_var, values=type_options, width=28).grid(
            row=3, column=1, sticky=tk.W, pady=2)
        
        # Safety Level
        ttk.Label(parent, text="Safety Level:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.safety_level_var = tk.StringVar(value=self.existing_data.get('safety_level', 'QM'))
        safety_options = ['QM', 'ASIL A', 'ASIL B', 'ASIL C', 'ASIL D']
        ttk.Combobox(parent, textvariable=self.safety_level_var, values=safety_options, width=28).grid(
            row=4, column=1, sticky=tk.W, pady=2)
        
        # Location
        ttk.Label(parent, text="Location:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.location_var = tk.StringVar(value=self.existing_data.get('location', 'Internal'))
        location_options = ['Internal', 'External']
        ttk.Combobox(parent, textvariable=self.location_var, values=location_options, width=28).grid(
            row=5, column=1, sticky=tk.W, pady=2)
        
        # Trust Zone
        ttk.Label(parent, text="Trust Zone:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.trust_zone_var = tk.StringVar(value=self.existing_data.get('trust_zone', 'Standard'))
        trust_options = ['Critical', 'Boundary', 'Standard', 'Untrusted']
        ttk.Combobox(parent, textvariable=self.trust_zone_var, values=trust_options, width=28).grid(
            row=6, column=1, sticky=tk.W, pady=2)
        
        # Interface details section
        ttk.Label(parent, text="Interface Details", font=("TkDefaultFont", 12, "bold")).grid(
            row=7, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))
        
        # Interfaces (with guidance)
        ttk.Label(parent, text="Interfaces:").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.interfaces_var = tk.StringVar(value=self.existing_data.get('interfaces', ''))
        ttk.Entry(parent, textvariable=self.interfaces_var, width=30).grid(
            row=8, column=1, sticky=tk.W, pady=2)
        ttk.Label(parent, text="(Separate with | e.g., CAN|FlexRay|Ethernet)").grid(
            row=9, column=1, sticky=tk.W, pady=(0, 5))
        
        # Access Points
        ttk.Label(parent, text="Access Points:").grid(row=10, column=0, sticky=tk.W, pady=2)
        self.access_points_var = tk.StringVar(value=self.existing_data.get('access_points', ''))
        ttk.Entry(parent, textvariable=self.access_points_var, width=30).grid(
            row=10, column=1, sticky=tk.W, pady=2)
        ttk.Label(parent, text="(Separate with | e.g., OBD-II|Debug Port|USB)").grid(
            row=11, column=1, sticky=tk.W, pady=(0, 5))
        
        # Data Types
        ttk.Label(parent, text="Data Types:").grid(row=12, column=0, sticky=tk.W, pady=2)
        self.data_types_var = tk.StringVar(value=self.existing_data.get('data_types', ''))
        ttk.Entry(parent, textvariable=self.data_types_var, width=30).grid(
            row=12, column=1, sticky=tk.W, pady=2)
        ttk.Label(parent, text="(Separate with | e.g., Control Commands|Sensor Data)").grid(
            row=13, column=1, sticky=tk.W, pady=(0, 5))
        
        # Connected To
        ttk.Label(parent, text="Connected To:").grid(row=14, column=0, sticky=tk.W, pady=2)
        self.connected_to_var = tk.StringVar(value=self.existing_data.get('connected_to', ''))
        ttk.Entry(parent, textvariable=self.connected_to_var, width=30).grid(
            row=14, column=1, sticky=tk.W, pady=2)
        ttk.Label(parent, text="(Separate with | e.g., ECU001|ECU002)").grid(
            row=15, column=1, sticky=tk.W, pady=(0, 5))
        
        # Help notes
        help_frame = ttk.LabelFrame(parent, text="Help")
        help_frame.grid(row=16, column=0, columnspan=2, sticky=tk.EW, pady=20)
        
        help_text = (
            "* Component ID should be unique (e.g., ECU001, SNS001)\n"
            "* Interfaces are communication protocols (CAN, FlexRay, etc.)\n"
            "* Access Points are physical interfaces (OBD-II, Debug Port, etc.)\n"
            "* Data Types describe the nature of data handled\n"
            "* Connected To lists the Component IDs this component connects to"
        )
        
        ttk.Label(help_frame, text=help_text, wraplength=500, justify=tk.LEFT).pack(
            padx=10, pady=10)
    
    def save_component(self):
        """Validate and save the component"""
        # Validate fields
        if not self.validate_fields():
            return
        
        # Collect data
        component_data = {
            'component_id': self.component_id_var.get().strip(),
            'name': self.name_var.get().strip(),
            'type': self.type_var.get().strip(),
            'safety_level': self.safety_level_var.get().strip(),
            'location': self.location_var.get().strip(),
            'trust_zone': self.trust_zone_var.get().strip(),
            'interfaces': self.interfaces_var.get().strip(),
            'access_points': self.access_points_var.get().strip(),
            'data_types': self.data_types_var.get().strip(),
            'connected_to': self.connected_to_var.get().strip()
        }
        
        # Call the save callback with the data
        self.on_save(component_data)
        
        # Close the dialog
        self.destroy()
    
    def validate_fields(self) -> bool:
        """Validate all required fields"""
        # Check required fields
        required_fields = [
            (self.component_id_var.get().strip(), "Component ID"),
            (self.name_var.get().strip(), "Component Name"),
            (self.type_var.get().strip(), "Type"),
            (self.safety_level_var.get().strip(), "Safety Level"),
            (self.location_var.get().strip(), "Location"),
            (self.trust_zone_var.get().strip(), "Trust Zone")
        ]
        
        for value, field_name in required_fields:
            if not value:
                messagebox.showerror("Validation Error", f"{field_name} is required.")
                return False
        
        # Validate component ID format
        component_id = self.component_id_var.get().strip()
        if not (3 <= len(component_id) <= 10):
            messagebox.showerror(
                "Validation Error", 
                "Component ID should be between 3 and 10 characters."
            )
            return False
        
        return True
