#!/usr/bin/env python3
"""
QuickTARA GUI
A desktop interface for automotive threat analysis and risk assessment
Using Tkinter for better compatibility and no external dependencies
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import pandas as pd

# Import core QuickTARA functionality
from quicktara import load_components, analyze_threats, write_report

class AnalysisThread(threading.Thread):
    """Background thread for running analysis"""
    def __init__(self, input_file: Path, callback):
        super().__init__()
        self.input_file = input_file
        self.callback = callback
        self.error = None
        self.result = None

    def run(self):
        try:
            components = load_components(self.input_file)
            threats = analyze_threats(components)
            self.result = {
                'components': components,
                'threats': threats
            }
        except Exception as e:
            self.error = str(e)
        finally:
            self.callback()

class ComponentTable(ttk.Treeview):
    """Table widget for displaying components"""
    def __init__(self, parent):
        columns = ('id', 'name', 'type', 'safety', 'interfaces', 
                  'access', 'data', 'location', 'trust', 'connected')
        super().__init__(parent, columns=columns, show='headings')
        
        # Configure columns
        self.heading('id', text='Component ID')
        self.heading('name', text='Name')
        self.heading('type', text='Type')
        self.heading('safety', text='Safety Level')
        self.heading('interfaces', text='Interfaces')
        self.heading('access', text='Access Points')
        self.heading('data', text='Data Types')
        self.heading('location', text='Location')
        self.heading('trust', text='Trust Zone')
        self.heading('connected', text='Connected To')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.yview)
        self.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        for col in columns:
            self.column(col, width=100)

    def load_data(self, data: pd.DataFrame):
        # Clear existing items
        for item in self.get_children():
            self.delete(item)
            
        # Add new data
        for _, row in data.iterrows():
            values = [str(row[col]) for col in row.index]
            self.insert('', tk.END, values=values)

class ResultText(tk.Text):
    """Text widget for displaying analysis results"""
    def __init__(self, parent):
        super().__init__(parent, wrap=tk.WORD, height=20)
        self.config(state=tk.DISABLED)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.yview)
        self.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def set_text(self, text: str):
        self.config(state=tk.NORMAL)
        self.delete(1.0, tk.END)
        self.insert(tk.END, text)
        self.config(state=tk.DISABLED)

class MainWindow:
    """Main application window"""
    def __init__(self, root):
        self.root = root
        self.root.title("QuickTARA - Automotive Security Analysis")
        self.root.geometry("1000x800")
        self.setup_ui()

    def setup_ui(self):
        # Create main menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open CSV", command=self.open_file)
        file_menu.add_command(label="Save Report", command=self.save_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # Components tab
        components_frame = ttk.Frame(notebook)
        notebook.add(components_frame, text='Components')
        
        # Add component table
        self.component_table = ComponentTable(components_frame)
        self.component_table.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(components_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Add Component", 
                  command=self.add_component).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Component", 
                  command=self.edit_component).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Run Analysis", 
                  command=self.run_analysis).pack(side=tk.RIGHT, padx=5)

        # Analysis tab
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text='Analysis Results')
        
        # Add progress bar
        self.progress = ttk.Progressbar(analysis_frame, mode='indeterminate')
        self.progress.pack(fill='x', padx=5, pady=5)
        
        # Add results view
        self.results_view = ResultText(analysis_frame)
        self.results_view.pack(expand=True, fill='both', padx=5, pady=5)

    def open_file(self):
        file_name = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if file_name:
            try:
                data = pd.read_csv(file_name)
                self.component_table.load_data(data)
                self.current_file = Path(file_name)
                messagebox.showinfo("Success", "File loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def save_report(self):
        if not hasattr(self, 'report_data'):
            messagebox.showwarning("Warning", "No analysis results to save!")
            return

        file_name = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[
                ("PDF Files", "*.pdf"),
                ("Excel Files", "*.xlsx"),
                ("JSON Files", "*.json")
            ]
        )
        if file_name:
            try:
                write_report(self.report_data['components'], 
                           self.report_data['threats'],
                           Path(file_name))
                messagebox.showinfo("Success", "Report saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {str(e)}")

    def run_analysis(self):
        if not hasattr(self, 'current_file'):
            messagebox.showwarning("Warning", "Please load a CSV file first!")
            return

        self.progress.start()
        self.results_view.set_text("Analysis in progress...")
        
        def analysis_complete():
            self.progress.stop()
            if self.analysis_thread.error:
                messagebox.showerror("Error", 
                                   f"Analysis failed: {self.analysis_thread.error}")
                self.results_view.set_text(f"Analysis failed: {self.analysis_thread.error}")
            else:
                self.report_data = self.analysis_thread.result
                summary = self.generate_summary(self.report_data)
                self.results_view.set_text(summary)
                messagebox.showinfo("Success", "Analysis completed successfully!")

        self.analysis_thread = AnalysisThread(self.current_file, analysis_complete)
        self.analysis_thread.start()

    def generate_summary(self, report_data: Dict) -> str:
        components = report_data['components']
        total_threats = sum(len(c.get('threats', [])) 
                          for c in components.values())
        
        summary = [
            "Analysis Results Summary",
            "=====================\n",
            f"Total Components: {len(components)}",
            f"Total Threats Identified: {total_threats}\n",
            "Component Details:"
        ]
        
        for comp_id, comp in components.items():
            threats = comp.get('threats', [])
            summary.extend([
                f"\n{comp['name']} ({comp_id})",
                f"Type: {comp['type']}",
                f"Safety Level: {comp['safety_level']}",
                f"Number of Threats: {len(threats)}",
                "Top Threats:"
            ])
            
            for threat in threats[:3]:  # Show top 3 threats
                summary.append(f"- {threat['name']}")
        
        return '\n'.join(summary)

    def add_component(self):
        # TODO: Implement component addition dialog
        messagebox.showinfo("Info", "Component addition coming soon!")

    def edit_component(self):
        # TODO: Implement component editing dialog
        messagebox.showinfo("Info", "Component editing coming soon!")

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
