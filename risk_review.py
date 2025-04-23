"""
Risk Review Module for QuickTARA
Implements manual review and refinement of risk treatment decisions
before final TARA report generation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Any, Tuple
import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
from risk_acceptance import AcceptanceDecision, RiskSeverity, StakeholderConcern

@dataclass
class ReviewDecision:
    """Records a manual review decision for a risk treatment"""
    original_decision: AcceptanceDecision
    final_decision: AcceptanceDecision
    reviewer: str
    justification: str
    additional_notes: str = ""
    review_date: str = ""
    evidence_references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary"""
        return {
            'original_decision': self.original_decision.value,
            'final_decision': self.final_decision.value,
            'reviewer': self.reviewer,
            'justification': self.justification,
            'additional_notes': self.additional_notes,
            'review_date': self.review_date,
            'evidence_references': self.evidence_references
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReviewDecision':
        """Create from dictionary"""
        return cls(
            original_decision=AcceptanceDecision(data.get('original_decision', 'Mitigate')),
            final_decision=AcceptanceDecision(data.get('final_decision', 'Mitigate')),
            reviewer=data.get('reviewer', ''),
            justification=data.get('justification', ''),
            additional_notes=data.get('additional_notes', ''),
            review_date=data.get('review_date', ''),
            evidence_references=data.get('evidence_references', [])
        )

def load_review_decisions(file_path: Path) -> Dict[str, Dict[str, ReviewDecision]]:
    """Load existing review decisions from file"""
    if not file_path.exists():
        return {}
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        results = {}
        for comp_id, threats in data.items():
            results[comp_id] = {}
            for threat_id, decision_data in threats.items():
                results[comp_id][threat_id] = ReviewDecision.from_dict(decision_data)
        
        return results
    except Exception as e:
        print(f"Error loading review decisions: {e}")
        return {}

def save_review_decisions(decisions: Dict[str, Dict[str, ReviewDecision]], file_path: Path) -> None:
    """Save review decisions to file"""
    try:
        # Convert to serializable format
        serialized = {}
        for comp_id, threats in decisions.items():
            serialized[comp_id] = {}
            for threat_id, decision in threats.items():
                serialized[comp_id][threat_id] = decision.to_dict()
        
        with open(file_path, 'w') as f:
            json.dump(serialized, f, indent=2)
    except Exception as e:
        print(f"Error saving review decisions: {e}")

class ReviewDialog(tk.Toplevel):
    """Dialog for reviewing risk treatment decisions"""
    def __init__(self, parent, component_name, threat_name, risk_data, 
                 original_decision=None, on_save=None):
        super().__init__(parent)
        self.title(f"Review Risk Treatment - {component_name}")
        self.geometry("700x650")
        self.resizable(True, True)
        
        self.component_name = component_name
        self.threat_name = threat_name
        self.risk_data = risk_data
        self.original_decision = original_decision or AcceptanceDecision.MITIGATE
        self.on_save = on_save
        
        self.review_decision = None
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Create the dialog UI"""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Component and threat info
        info_frame = ttk.LabelFrame(main_frame, text="Risk Information", padding="5")
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="Component:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=self.component_name, font=("", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Threat:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=self.threat_name, font=("", 10, "bold")).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Severity:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=self.risk_data.get('risk_severity', "Medium"), font=("", 10, "bold")).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Residual Risk:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        residual_risk = self.risk_data.get('residual_risk', 0.3)
        ttk.Label(info_frame, text=f"{residual_risk:.1%}", font=("", 10, "bold")).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Calculated justification
        ttk.Label(info_frame, text="Automated Justification:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        justification_text = tk.Text(info_frame, height=3, width=50, wrap=tk.WORD)
        justification_text.grid(row=4, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        justification_text.insert(tk.END, self.risk_data.get('justification', ""))
        justification_text.config(state=tk.DISABLED)
        
        # Original vs. final decision
        decision_frame = ttk.LabelFrame(main_frame, text="Treatment Decision", padding="5")
        decision_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(decision_frame, text="Original Decision:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(decision_frame, text=self.original_decision.value, font=("", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(decision_frame, text="Final Decision:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Decision dropdown
        self.decision_var = tk.StringVar()
        decision_options = [decision.value for decision in AcceptanceDecision]
        self.decision_dropdown = ttk.Combobox(decision_frame, textvariable=self.decision_var, values=decision_options, width=20)
        self.decision_dropdown.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        self.decision_dropdown.current(decision_options.index(self.original_decision.value))
        
        # Reviewer info
        reviewer_frame = ttk.LabelFrame(main_frame, text="Review Information", padding="5")
        reviewer_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(reviewer_frame, text="Reviewer Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.reviewer_entry = ttk.Entry(reviewer_frame, width=30)
        self.reviewer_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        
        ttk.Label(reviewer_frame, text="Review Date:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.date_entry = ttk.Entry(reviewer_frame, width=30)
        self.date_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        
        # Create today's date in YYYY-MM-DD format
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)
        
        # Justification and notes
        justification_frame = ttk.LabelFrame(main_frame, text="Justification and Notes", padding="5")
        justification_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(justification_frame, text="Review Justification:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.justification_text = tk.Text(justification_frame, height=5, width=60, wrap=tk.WORD)
        self.justification_text.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=2)
        
        ttk.Label(justification_frame, text="Additional Notes:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.notes_text = tk.Text(justification_frame, height=5, width=60, wrap=tk.WORD)
        self.notes_text.grid(row=3, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=2)
        
        ttk.Label(justification_frame, text="Evidence References (one per line):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.evidence_text = tk.Text(justification_frame, height=3, width=60, wrap=tk.WORD)
        self.evidence_text.grid(row=5, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=2)
        
        # Configure row/column weights for expansion
        justification_frame.columnconfigure(0, weight=1)
        for i in range(6):
            justification_frame.rowconfigure(i, weight=1 if i in [1, 3, 5] else 0)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Save Review", command=self.save_review).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def load_data(self):
        """Load existing review data if available"""
        if hasattr(self, 'review_decision') and self.review_decision:
            self.decision_var.set(self.review_decision.final_decision.value)
            self.reviewer_entry.insert(0, self.review_decision.reviewer)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, self.review_decision.review_date)
            self.justification_text.insert(tk.END, self.review_decision.justification)
            self.notes_text.insert(tk.END, self.review_decision.additional_notes)
            self.evidence_text.insert(tk.END, "\n".join(self.review_decision.evidence_references))
    
    def save_review(self):
        """Save the review decision"""
        # Validate inputs
        reviewer = self.reviewer_entry.get().strip()
        if not reviewer:
            messagebox.showerror("Error", "Reviewer name is required")
            return
        
        justification = self.justification_text.get("1.0", tk.END).strip()
        if not justification:
            messagebox.showerror("Error", "Review justification is required")
            return
        
        # Get other values
        final_decision = AcceptanceDecision(self.decision_var.get())
        review_date = self.date_entry.get().strip()
        additional_notes = self.notes_text.get("1.0", tk.END).strip()
        evidence_lines = self.evidence_text.get("1.0", tk.END).strip().split("\n")
        evidence_references = [line for line in evidence_lines if line.strip()]
        
        # Create review decision
        self.review_decision = ReviewDecision(
            original_decision=self.original_decision,
            final_decision=final_decision,
            reviewer=reviewer,
            justification=justification,
            additional_notes=additional_notes,
            review_date=review_date,
            evidence_references=evidence_references
        )
        
        # Call the save callback if provided
        if self.on_save:
            self.on_save(self.review_decision)
        
        self.destroy()

class ReviewManager:
    """Manages the risk treatment review process"""
    def __init__(self, parent_window, report_data, base_path):
        self.parent = parent_window
        self.report_data = report_data
        self.base_path = Path(base_path)
        self.review_file = self.base_path / "risk_reviews.json"
        
        # Load existing reviews if available
        self.review_decisions = load_review_decisions(self.review_file)
        
        # Track which risks have been reviewed
        self.reviewed_risks = set()
        for comp_id, threats in self.review_decisions.items():
            for threat_id in threats:
                self.reviewed_risks.add(f"{comp_id}:{threat_id}")
    
    def launch_review_process(self):
        """Launch the main review window"""
        self.review_window = tk.Toplevel(self.parent)
        self.review_window.title("Risk Treatment Review")
        self.review_window.geometry("1000x700")
        self.setup_review_ui()
    
    def setup_review_ui(self):
        """Set up the main review UI"""
        # Main container
        main_frame = ttk.Frame(self.review_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(header_frame, text="Risk Treatment Review Process", 
                 font=("", 14, "bold")).pack(side=tk.LEFT)
        
        # Status info
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_var = tk.StringVar()
        self.update_status()
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        # Review table
        table_frame = ttk.LabelFrame(main_frame, text="Risks Requiring Review", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview for risks
        columns = ('component', 'threat', 'severity', 'decision', 'status')
        self.risk_table = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configure column headings
        self.risk_table.heading('component', text='Component')
        self.risk_table.heading('threat', text='Threat')
        self.risk_table.heading('severity', text='Risk Severity')
        self.risk_table.heading('decision', text='Suggested Decision')
        self.risk_table.heading('status', text='Review Status')
        
        # Configure column widths
        self.risk_table.column('component', width=150)
        self.risk_table.column('threat', width=200)
        self.risk_table.column('severity', width=100)
        self.risk_table.column('decision', width=150)
        self.risk_table.column('status', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.risk_table.yview)
        self.risk_table.configure(yscrollcommand=scrollbar.set)
        
        # Pack table and scrollbar
        self.risk_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to open review dialog
        self.risk_table.bind("<Double-1>", self.open_review_dialog)
        
        # Populate table
        self.populate_risk_table()
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Review Selected", 
                  command=self.review_selected).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Save All Reviews", 
                  command=self.save_all_reviews).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.close_review).pack(side=tk.RIGHT, padx=5)
    
    def populate_risk_table(self):
        """Populate the risk table with data"""
        # Clear existing items
        for item in self.risk_table.get_children():
            self.risk_table.delete(item)
        
        # Add components and their threats
        for comp_id, comp_data in self.report_data['components'].items():
            if not isinstance(comp_data, dict):
                continue
                
            comp_name = comp_data.get('name', comp_id)
            
            # Get risk acceptance data
            risk_acceptance = comp_data.get('risk_acceptance', {})
            
            for threat_name, assessment in risk_acceptance.items():
                # Get risk severity and decision
                severity = assessment.get('risk_severity', 'Medium')
                decision = assessment.get('decision', 'Mitigate')
                
                # Check if reviewed
                review_status = "Reviewed" if f"{comp_id}:{threat_name}" in self.reviewed_risks else "Pending"
                
                # Add to table
                self.risk_table.insert('', tk.END, values=(
                    comp_name, threat_name, severity, decision, review_status
                ))
    
    def update_status(self):
        """Update the status information"""
        total_risks = 0
        reviewed_risks = 0
        
        # Count risks and reviews
        for comp_id, comp_data in self.report_data['components'].items():
            if isinstance(comp_data, dict):
                risk_acceptance = comp_data.get('risk_acceptance', {})
                total_risks += len(risk_acceptance)
                
                for threat_name in risk_acceptance:
                    if f"{comp_id}:{threat_name}" in self.reviewed_risks:
                        reviewed_risks += 1
        
        self.status_var.set(f"Total risks: {total_risks} | Reviewed: {reviewed_risks} | Pending: {total_risks - reviewed_risks}")
    
    def review_selected(self):
        """Open review dialog for the selected risk"""
        selected_items = self.risk_table.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a risk to review")
            return
        
        # Get the first selected item
        self.open_review_dialog(item=selected_items[0])
    
    def open_review_dialog(self, event=None, item=None):
        """Open the review dialog for a risk"""
        # Get selected item
        if item is None:
            if event is None:
                return
            item = self.risk_table.identify('item', event.x, event.y)
            if not item:
                return
        
        # Get item values
        values = self.risk_table.item(item, 'values')
        if not values:
            return
        
        component_name, threat_name, severity, decision, status = values
        
        # Find component and threat in data
        comp_id = None
        threat_data = None
        
        for cid, comp_data in self.report_data['components'].items():
            if not isinstance(comp_data, dict):
                continue
                
            if comp_data.get('name') == component_name:
                comp_id = cid
                if 'risk_acceptance' in comp_data and threat_name in comp_data['risk_acceptance']:
                    threat_data = comp_data['risk_acceptance'][threat_name]
                break
        
        if not comp_id or not threat_data:
            messagebox.showerror("Error", "Could not find risk data")
            return
        
        # Get existing review if available
        existing_review = None
        if comp_id in self.review_decisions and threat_name in self.review_decisions[comp_id]:
            existing_review = self.review_decisions[comp_id][threat_name]
        
        # Create the review dialog
        original_decision = AcceptanceDecision(decision)
        dialog = ReviewDialog(
            self.review_window, component_name, threat_name, threat_data, 
            original_decision=original_decision,
            on_save=lambda decision: self.save_review(comp_id, threat_name, decision)
        )
        
        # Set existing review data if available
        if existing_review:
            dialog.review_decision = existing_review
            dialog.load_data()
        
        # Make dialog modal
        dialog.transient(self.review_window)
        dialog.grab_set()
        self.review_window.wait_window(dialog)
    
    def save_review(self, comp_id, threat_name, review_decision):
        """Save a single review decision"""
        # Initialize dictionaries if needed
        if comp_id not in self.review_decisions:
            self.review_decisions[comp_id] = {}
        
        # Save the decision
        self.review_decisions[comp_id][threat_name] = review_decision
        
        # Mark as reviewed
        self.reviewed_risks.add(f"{comp_id}:{threat_name}")
        
        # Update UI
        self.update_status()
        self.populate_risk_table()
    
    def save_all_reviews(self):
        """Save all review decisions to file"""
        save_review_decisions(self.review_decisions, self.review_file)
        messagebox.showinfo("Success", f"Saved {len(self.reviewed_risks)} review decisions to {self.review_file}")
    
    def close_review(self):
        """Close the review window"""
        # Check if all risks have been reviewed
        total_risks = 0
        for comp_id, comp_data in self.report_data['components'].items():
            if isinstance(comp_data, dict) and 'risk_acceptance' in comp_data:
                total_risks += len(comp_data['risk_acceptance'])
        
        if len(self.reviewed_risks) < total_risks:
            if not messagebox.askyesno("Warning", 
                                    f"{total_risks - len(self.reviewed_risks)} risks have not been reviewed. Close anyway?"):
                return
        
        # Save reviews before closing
        if self.reviewed_risks:
            if messagebox.askyesno("Save Reviews", "Save review decisions before closing?"):
                self.save_all_reviews()
        
        self.review_window.destroy()
    
    def get_review_decisions(self) -> Dict[str, Dict[str, ReviewDecision]]:
        """Get the current review decisions"""
        return self.review_decisions


def apply_review_decisions(report_data: Dict, review_decisions: Dict[str, Dict[str, ReviewDecision]]) -> Dict:
    """Apply review decisions to the report data"""
    updated_report = report_data.copy()
    
    # Apply decisions to each component and threat
    for comp_id, threats in review_decisions.items():
        if comp_id not in updated_report['components']:
            continue
        
        component = updated_report['components'][comp_id]
        if not isinstance(component, dict) or 'risk_acceptance' not in component:
            continue
        
        for threat_name, decision in threats.items():
            if threat_name not in component['risk_acceptance']:
                continue
            
            # Update decision in report
            assessment = component['risk_acceptance'][threat_name]
            
            # Update with review decision
            assessment['decision'] = decision.final_decision.value
            assessment['justification'] = decision.justification
            assessment['reviewer'] = decision.reviewer
            assessment['review_date'] = decision.review_date
            assessment['additional_notes'] = decision.additional_notes
            assessment['evidence_references'] = decision.evidence_references
            assessment['review_status'] = 'Reviewed'
    
    return updated_report

def format_review_decision(decision: ReviewDecision) -> str:
    """Format a review decision for display in reports"""
    result = []
    
    result.append(f"Decision: {decision.final_decision.value}")
    if decision.final_decision != decision.original_decision:
        result.append(f"(Changed from: {decision.original_decision.value})")
    
    result.append(f"\nJustification: {decision.justification}")
    
    if decision.additional_notes:
        result.append(f"\nAdditional Notes: {decision.additional_notes}")
    
    result.append(f"\nReviewed by: {decision.reviewer}")
    result.append(f"Review Date: {decision.review_date}")
    
    if decision.evidence_references:
        result.append("\nEvidence References:")
        for ref in decision.evidence_references:
            result.append(f"- {ref}")
    
    return "\n".join(result)
