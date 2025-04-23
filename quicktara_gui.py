#!/usr/bin/env python3
"""
QuickTARA GUI
A desktop interface for automotive threat analysis and risk assessment
Using Tkinter for better compatibility and no external dependencies
"""

import sys
import os
import csv
from pathlib import Path
from typing import List, Dict, Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import pandas as pd
from datetime import datetime

# Import core QuickTARA functionality
from quicktara import load_components, analyze_threats, write_report

# Import component dialog
from component_dialog import ComponentDialog

# Import analysis modules
from attacker_feasibility import AttackerProfile, AttackerAssessment
from risk_acceptance import RiskAcceptanceAssessment
from risk_review import ReviewManager, apply_review_decisions

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
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # Components tab
        components_frame = ttk.Frame(self.notebook)
        self.notebook.add(components_frame, text='Components')
        
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
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text='Analysis Results')
        
        # Button frame for analysis tab
        analysis_button_frame = ttk.Frame(analysis_frame)
        analysis_button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(analysis_button_frame, text="Review Risk Treatments", 
                  command=self.review_risk_treatments).pack(side=tk.LEFT, padx=5)
        ttk.Button(analysis_button_frame, text="Generate Final Report", 
                  command=self.generate_final_report).pack(side=tk.LEFT, padx=5)
        
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

        # Switch to analysis tab
        self.root.update()
        self.notebook.select(1)  # Select the Analysis Results tab
        
        # Start progress bar
        self.progress.start()
        self.results_view.set_text("Analysis in progress...\nThis may take a few moments depending on the number of components.")
        self.root.update()
        
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
                
                # Create default report files
                try:
                    # Store original report data for later use
                    self.original_report_data = {
                        'components': self.report_data['components'],
                        'threats': self.report_data['threats'],
                        'generated_at': datetime.now().isoformat(),
                        'summary': {
                            'total_components': len(self.report_data['components']),
                            'total_threats': sum(len(comp_data.get('threats', [])) 
                                             for comp_id, comp_data in self.report_data['threats'].items()),
                            'high_risk_threats': sum(
                                1 for comp_data in self.report_data['threats'].values()
                                for threat in comp_data.get('threats', [])
                                if any(score >= 4 for score in threat.get('impact', {}).values())
                            )
                        }
                    }
                    
                    # Generate preliminary reports
                    base_path = self.current_file.parent / 'preliminary_report'
                    write_report(self.report_data['components'], self.report_data['threats'], base_path)
                    report_msg = f"Analysis completed successfully!\n\nPreliminary reports saved to:\n{base_path}.txt\n{base_path}.json\n\nPlease review risk treatment decisions before generating the final report."
                    messagebox.showinfo("Success", report_msg)
                except Exception as e:
                    messagebox.showwarning("Warning", f"Analysis completed but failed to save preliminary reports: {str(e)}")

        # Run analysis in background thread
        self.analysis_thread = AnalysisThread(self.current_file, analysis_complete)
        self.analysis_thread.start()

    def generate_summary(self, report_data: Dict) -> str:
        components = report_data['components']
        threats_data = report_data['threats']
        
        # Calculate total threats across all components
        total_threats = sum(len(comp_data.get('threats', [])) 
                           for comp_id, comp_data in threats_data.items())
        
        # Count high-risk threats
        high_risk_count = sum(
            1 for comp_data in threats_data.values()
            for threat in comp_data.get('threats', [])
            if any(score >= 4 for score in threat.get('impact', {}).values())
        )
        
        # Count critical components
        critical_components = sum(1 for comp in components.values() 
                               if getattr(comp, 'trust_zone', None) and 
                               comp.trust_zone.value == 'Critical')
        
        summary = [
            "QuickTARA Analysis Results",
            "=========================\n",
            f"Total Components: {len(components)}",
            f"Critical Components: {critical_components}",
            f"Total Threats Identified: {total_threats}",
            f"High-Risk Threats: {high_risk_count}\n",
            "Component Threat Summary:"
        ]
        
        # Create summary for each component
        for comp_id, comp_threats in threats_data.items():
            if comp_id not in components:
                continue
                
            comp = components[comp_id]
            comp_name = getattr(comp, 'name', comp_id)
            threat_list = comp_threats.get('threats', [])
            stride_analysis = comp_threats.get('stride_analysis', {})
            
            # Count high severity threats for this component
            high_severity = sum(
                1 for t in threat_list
                if any(score >= 4 for score in t.get('impact', {}).values())
            )
            
            # Count high risk STRIDE categories
            high_risk_stride = sum(
                1 for cat, data in stride_analysis.items()
                if data.get('risk_level') == 'High'
            )
            
            summary.extend([
                f"\n{comp_name} ({comp_id})",
                f"Type: {getattr(comp, 'type', '').value if hasattr(comp, 'type') else comp_threats.get('type', '')}",
                f"Safety Level: {getattr(comp, 'safety_level', '').value if hasattr(comp, 'safety_level') else comp_threats.get('safety_level', '')}",
                f"Total Threats: {len(threat_list)}",
                f"High Severity Threats: {high_severity}",
                f"High Risk STRIDE Categories: {high_risk_stride}",
                "Top Threats:"
            ])
            
            # List top threats by impact severity
            sorted_threats = sorted(
                threat_list, 
                key=lambda t: max(t.get('impact', {}).values() or [0]), 
                reverse=True
            )
            
            for threat in sorted_threats[:3]:  # Show top 3 threats
                impacts = threat.get('impact', {})
                max_impact = max(impacts.values()) if impacts else 0
                impact_str = ", ".join([f"{k}: {v}" for k, v in impacts.items()])
                summary.append(f"- {threat['name']} (Impact: {impact_str})")
            
            # Add cybersecurity goals for this component
            if 'cybersecurity_goals' in comp_threats and comp_threats['cybersecurity_goals']:
                summary.append("\nCybersecurity Goals:")
                
                # Get top threats by impact
                top_threats = sorted_threats[:2]  # Use top 2 threats
                top_threat_names = [t['name'] for t in top_threats]
                
                # Show goals for top threats
                goals_shown = 0
                for threat_name, mappings in comp_threats['cybersecurity_goals'].items():
                    # Focus on top threats first
                    if threat_name in top_threat_names or goals_shown < 1:
                        goals_shown += 1
                        summary.append(f"  For threat: {threat_name}")
                        
                        # Show top goals for this threat
                        for mapping in mappings[:2]:  # Show only top 2 goals for readability
                            summary.append(f"  - {mapping.goal.value} (Relevance: {mapping.relevance}/5)")
                            summary.append(f"    {mapping.description}")
                            # Show a single top requirement
                            if mapping.requirements:
                                summary.append(f"    Requirement: {mapping.requirements[0]}")
                        
                        summary.append("")  # Add blank line between threats
                    
                    # Limit to showing goals for at most 2 threats
                    if goals_shown >= 2:
                        break
            
            # Add feasibility assessments
            if 'feasibility_assessments' in comp_threats and comp_threats['feasibility_assessments']:
                summary.append("\nAttacker Feasibility Assessments:")
                
                # Get top threats by impact
                top_threats = sorted_threats[:2] if sorted_threats else []  # Use top 2 threats
                top_threat_names = [t['name'] for t in top_threats]
                
                # Show assessments for top threats
                assessments_shown = 0
                for threat_name, assessment in comp_threats['feasibility_assessments'].items():
                    # Focus on top threats first
                    if threat_name in top_threat_names or assessments_shown < 1:
                        assessments_shown += 1
                        
                        summary.append(f"  For threat: {threat_name}")
                        # Check if assessment is an AttackerAssessment object or a dictionary
                        if hasattr(assessment, 'feasibility'):
                            # It's an AttackerAssessment object
                            summary.append(f"  Feasibility: {assessment.feasibility.feasibility_level} ({assessment.feasibility.overall_score}/5)")
                            
                            # Add key factors
                            summary.append("  Attack Difficulty Factors:")
                            summary.append(f"  - Technical Capability: {assessment.feasibility.technical_capability}/5")
                            summary.append(f"  - Knowledge Required: {assessment.feasibility.knowledge_required}/5")
                            summary.append(f"  - Resources Needed: {assessment.feasibility.resources_needed}/5")
                        else:
                            # It's a dictionary (already serialized)
                            summary.append(f"  Feasibility: {assessment.get('feasibility_level', 'N/A')} ({assessment.get('overall_score', 'N/A')}/5)")
                            
                            # Add key factors
                            summary.append("  Attack Difficulty Factors:")
                            summary.append(f"  - Technical Capability: {assessment.get('technical_capability', 'N/A')}/5")
                            summary.append(f"  - Knowledge Required: {assessment.get('knowledge_required', 'N/A')}/5")
                            summary.append(f"  - Resources Needed: {assessment.get('resources_needed', 'N/A')}/5")
                        
                        # Add top attacker profile
                        if hasattr(assessment, 'profiles'):
                            # It's an AttackerAssessment object
                            profiles = assessment.profiles
                            if profiles:
                                top_profile = max(profiles.items(), key=lambda x: x[1])[0]
                                profile_score = profiles[top_profile]
                                summary.append(f"  Most Relevant Attacker: {top_profile.value} ({profile_score}/5)")
                        elif 'profiles' in assessment:
                            # It's a dictionary
                            profiles = assessment['profiles']
                            if profiles:
                                top_profile = max(profiles.items(), key=lambda x: x[1])[0]
                                profile_score = profiles[top_profile]
                                summary.append(f"  Most Relevant Attacker: {top_profile} ({profile_score}/5)")
                        
                        # Add a sample of enabling and mitigating factors
                        if hasattr(assessment, 'enabling_factors') and assessment.enabling_factors:
                            # It's an AttackerAssessment object
                            summary.append("  Enabling Factor: " + assessment.enabling_factors[0])
                            
                        elif 'enabling_factors' in assessment and assessment['enabling_factors']:
                            # It's a dictionary
                            summary.append("  Enabling Factor: " + assessment['enabling_factors'][0])
                            
                        if hasattr(assessment, 'mitigating_factors') and assessment.mitigating_factors:
                            # It's an AttackerAssessment object
                            summary.append("  Mitigating Factor: " + assessment.mitigating_factors[0])
                            
                        elif 'mitigating_factors' in assessment and assessment['mitigating_factors']:
                            # It's a dictionary
                            summary.append("  Mitigating Factor: " + assessment['mitigating_factors'][0])
                        
                        summary.append("")  # Add blank line between assessments
                    
                    # Limit to showing assessments for at most 2 threats
                    if assessments_shown >= 2:
                        break
            
            # Add risk acceptance criteria for this component
            if 'risk_acceptance' in comp_threats and comp_threats['risk_acceptance']:
                summary.append("\nRisk Acceptance Criteria (Clause 14):")
                
                # Get top threats by impact
                top_threats = sorted_threats[:2] if sorted_threats else []  # Use top 2 threats
                top_threat_names = [t['name'] for t in top_threats]
                
                # Show assessments for top threats
                assessments_shown = 0
                for threat_name, assessment in comp_threats['risk_acceptance'].items():
                    # Focus on top threats first
                    if threat_name in top_threat_names or assessments_shown < 1:
                        assessments_shown += 1
                        
                        summary.append(f"  For threat: {threat_name}")
                        # Check if assessment is a RiskAcceptanceAssessment object or a dictionary
                        if hasattr(assessment, 'decision'):
                            # It's a RiskAcceptanceAssessment object
                            summary.append(f"  Decision: {assessment.decision.value}")
                            summary.append(f"  Risk Severity: {assessment.risk_severity.value}")
                            summary.append(f"  Residual Risk: {assessment.residual_risk:.1%}")
                            summary.append(f"  Justification: {assessment.justification}")
                            
                            # Show top conditions
                            if assessment.conditions:
                                summary.append("  Top Conditions:")
                                for condition in assessment.conditions[:2]:  # Show top 2 for readability
                                    summary.append(f"  - {condition}")
                        else:
                            # It's a dictionary (already serialized)
                            summary.append(f"  Decision: {assessment.get('decision', 'N/A')}")
                            summary.append(f"  Risk Severity: {assessment.get('risk_severity', 'N/A')}")
                            summary.append(f"  Residual Risk: {assessment.get('residual_risk', 0):.1%}")
                            summary.append(f"  Justification: {assessment.get('justification', 'N/A')}")
                            
                            # Show top conditions
                            if 'conditions' in assessment and assessment['conditions']:
                                summary.append("  Top Conditions:")
                                for condition in assessment['conditions'][:2]:  # Show top 2 for readability
                                    summary.append(f"  - {condition}")
                        
                        summary.append("")  # Add blank line between assessments
                    
                    # Limit to showing assessments for at most 2 threats
                    if assessments_shown >= 2:
                        break
        
        return '\n'.join(summary)

    def add_component(self):
        """Open dialog to add a new component"""
        # Check if we have a current file to add the component to
        if not hasattr(self, 'current_file'):
            if not self.create_new_file():
                return
        
        # Define callback for when component is saved
        def on_save(component_data):
            try:
                self.add_component_to_csv(component_data)
                messagebox.showinfo("Success", "Component added successfully!")
                # Reload the data to update the table
                data = pd.read_csv(self.current_file)
                self.component_table.load_data(data)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add component: {str(e)}")
        
        # Open the component dialog
        ComponentDialog(self.root, on_save=on_save)
    
    def create_new_file(self) -> bool:
        """Create a new CSV file if none exists"""
        file_name = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Create New Components File"
        )
        
        if not file_name:
            return False
        
        try:
            # Create a new CSV file with headers
            with open(file_name, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'component_id', 'name', 'type', 'safety_level', 'interfaces',
                    'access_points', 'data_types', 'location', 'trust_zone', 'connected_to'
                ])
            
            self.current_file = Path(file_name)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create file: {str(e)}")
            return False
    
    def add_component_to_csv(self, component_data: Dict):
        """Add a component to the current CSV file"""
        # First check if the component ID already exists
        try:
            existing_data = pd.read_csv(self.current_file)
            if component_data['component_id'] in existing_data['component_id'].values:
                raise ValueError(f"Component ID {component_data['component_id']} already exists")
            
            # Append to the CSV file
            with open(self.current_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    component_data['component_id'],
                    component_data['name'],
                    component_data['type'],
                    component_data['safety_level'],
                    component_data['interfaces'],
                    component_data['access_points'],
                    component_data['data_types'],
                    component_data['location'],
                    component_data['trust_zone'],
                    component_data['connected_to']
                ])
        except Exception as e:
            raise Exception(f"Failed to add component: {str(e)}")

    def edit_component(self):
        """Open dialog to edit an existing component"""
        # Check if we have a selected component
        selected_items = self.component_table.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a component to edit.")
            return
        
        # Get the selected component data
        selected_item = selected_items[0]
        values = self.component_table.item(selected_item, 'values')
        
        # Create a dictionary from the selected values
        columns = ['component_id', 'name', 'type', 'safety_level', 'interfaces',
                  'access_points', 'data_types', 'location', 'trust_zone', 'connected_to']
        component_data = {columns[i]: values[i] for i in range(len(columns))}
        
        # Define callback for when component is saved
        def on_save(updated_data):
            try:
                self.update_component_in_csv(component_data['component_id'], updated_data)
                messagebox.showinfo("Success", "Component updated successfully!")
                # Reload the data to update the table
                data = pd.read_csv(self.current_file)
                self.component_table.load_data(data)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update component: {str(e)}")
        
        # Open the component dialog in edit mode
        ComponentDialog(self.root, on_save=on_save, edit_mode=True, existing_data=component_data)
    
    def update_component_in_csv(self, original_id: str, updated_data: Dict):
        """Update a component in the current CSV file"""
        try:
            # Read the current data
            df = pd.read_csv(self.current_file)
            
            # Check if ID exists (should always be true at this point)
            if original_id not in df['component_id'].values:
                raise ValueError(f"Component ID {original_id} not found")
            
            # Check if new ID conflicts with another component
            if updated_data['component_id'] != original_id and \
               updated_data['component_id'] in df['component_id'].values:
                raise ValueError(f"Component ID {updated_data['component_id']} already exists")
            
            # Update the row
            idx = df.index[df['component_id'] == original_id].tolist()[0]
            df.loc[idx, 'component_id'] = updated_data['component_id']
            df.loc[idx, 'name'] = updated_data['name']
            df.loc[idx, 'type'] = updated_data['type']
            df.loc[idx, 'safety_level'] = updated_data['safety_level']
            df.loc[idx, 'interfaces'] = updated_data['interfaces']
            df.loc[idx, 'access_points'] = updated_data['access_points']
            df.loc[idx, 'data_types'] = updated_data['data_types']
            df.loc[idx, 'location'] = updated_data['location']
            df.loc[idx, 'trust_zone'] = updated_data['trust_zone']
            df.loc[idx, 'connected_to'] = updated_data['connected_to']
            
            # Write back to the file
            df.to_csv(self.current_file, index=False)
            
        except Exception as e:
            raise Exception(f"Failed to update component: {str(e)}")

    def review_risk_treatments(self):
        """Launch the risk treatment review process"""
        if not hasattr(self, 'original_report_data'):
            messagebox.showwarning("Warning", "Please run analysis first!")
            return
        
        # Create review manager
        review_manager = ReviewManager(
            self.root, 
            self.original_report_data, 
            self.current_file.parent
        )
        
        # Launch review process
        review_manager.launch_review_process()
        
        # Store review manager for access to decisions later
        self.review_manager = review_manager

    def generate_final_report(self):
        """Generate final report with manual review decisions"""
        if not hasattr(self, 'original_report_data'):
            messagebox.showwarning("Warning", "Please run analysis first!")
            return
        
        if not hasattr(self, 'review_manager'):
            if not messagebox.askyesno("Warning", 
                                    "No review process completed. Generate final report anyway?"):
                return
            # Create a default review manager
            self.review_manager = ReviewManager(
                self.root, 
                self.original_report_data, 
                self.current_file.parent
            )
        
        # Get review decisions
        review_decisions = self.review_manager.get_review_decisions()
        
        # Apply review decisions to report data
        final_report_data = apply_review_decisions(self.original_report_data, review_decisions)
        
        # Save final report
        file_name = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile="final_report",
            filetypes=[
                ("JSON Files", "*.json"),
                ("Excel Files", "*.xlsx"),
                ("PDF Files", "*.pdf"),
                ("Text Files", "*.txt")
            ],
            title="Save Final TARA Report"
        )
        
        if not file_name:
            return
        
        try:
            # Determine format based on extension
            ext = Path(file_name).suffix.lower()[1:]
            if ext in ('json', 'xlsx', 'pdf', 'txt'):
                format = 'json' if ext == 'json' else 'excel' if ext == 'xlsx' else 'pdf' if ext == 'pdf' else 'txt'
            else:
                format = 'json'  # Default to JSON
            
            # Write final report
            output_path = Path(file_name)
            components = self.original_report_data['components']
            threats = final_report_data['threats']
            
            write_report(components, threats, output_path.with_suffix(''))
            
            # Show success message
            messagebox.showinfo("Success", 
                             f"Final TARA report with reviewed risk treatments saved to {output_path}")
            
            # Add review info to report summary
            reviewed_count = sum(len(decisions) for comp_id, decisions in review_decisions.items())
            total_risks = sum(len(comp_data.get('risk_acceptance', {})) 
                            for comp_id, comp_data in components.items() 
                            if isinstance(comp_data, dict))
            
            review_summary = f"\n\nRisk Treatment Review Summary:\n"
            review_summary += f"Total risks: {total_risks}\n"
            review_summary += f"Manually reviewed: {reviewed_count}\n"
            
            # Update results view with review summary
            current_text = self.results_view.get("1.0", tk.END)
            self.results_view.config(state=tk.NORMAL)
            self.results_view.delete("1.0", tk.END)
            self.results_view.insert(tk.END, current_text.strip() + review_summary)
            self.results_view.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate final report: {str(e)}")

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
