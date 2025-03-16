"""
Export formats module for QuickTARA
Handles export to JSON, Excel, and PDF formats
"""

import json
from pathlib import Path
from typing import Dict
import pandas as pd
from fpdf import FPDF

class UTF8PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Add Unicode font support
        self.add_font('DejaVu', '', '/Library/Fonts/Arial Unicode.ttf', uni=True)
        self.set_font('DejaVu', '', 10)

def export_to_json(data: Dict, output_file: Path) -> None:
    """Export report data to JSON format"""
    with output_file.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def export_to_excel(data: Dict, output_file: Path) -> None:
    """Export report data to Excel format with multiple sheets"""
    # Create Excel writer
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Components overview sheet
        components_data = []
        for name, comp in data['components'].items():
            comp_row = {
                'Name': name,
                'Type': comp['type'],
                'Safety Level': comp['safety_level'],
                'Interfaces': '|'.join(comp['interfaces']),
                'Access Points': '|'.join(comp['access_points']),
                'Data Types': '|'.join(comp['data_types']),
                'Location': comp['location'],
                'Trust Zone': comp['trust_zone'],
                'Connected To': '|'.join(comp['connected_to'])
            }
            components_data.append(comp_row)
        
        pd.DataFrame(components_data).to_excel(writer, sheet_name='Components', index=False)
        
        # Threats sheet
        threats_data = []
        for comp_name, comp in data['components'].items():
            for threat in comp.get('threats', []):
                threat_row = {
                    'Component': comp_name,
                    'Threat': threat['name'],
                    'Impact Scores': str(threat['impact_scores']),
                    'Risk Scores': str(threat['risk_scores'])
                }
                if 'description' in threat:
                    threat_row['Description'] = threat.get('description', '')[:200]
                if 'mitigations' in threat:
                    threat_row['Mitigations'] = threat.get('mitigations', '')[:200]
                threats_data.append(threat_row)
        
        pd.DataFrame(threats_data).to_excel(writer, sheet_name='Threats', index=False)
        
        # Attack Chains sheet
        chains_data = []
        for comp_name, comp in data['components'].items():
            for threat in comp.get('threats', []):
                if 'attack_chains' in threat:
                    for chain in threat['attack_chains']:
                        chain_row = {
                            'Component': comp_name,
                            'Threat': threat['name'],
                            'Chain': ' -> '.join(chain['chain']),
                            'Risk Scores': str(chain['risk_scores'])
                        }
                        chains_data.append(chain_row)
        
        if chains_data:
            pd.DataFrame(chains_data).to_excel(writer, sheet_name='Attack Chains', index=False)

def export_to_pdf(data: Dict, output_file: Path) -> None:
    """Export report data to PDF format"""
    pdf = UTF8PDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('DejaVu', '', 16)
    pdf.cell(0, 10, 'QuickTARA Security Analysis Report', 0, 1, 'C')
    pdf.ln(10)
    
    # Components section
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(0, 10, 'Components Analysis', 0, 1, 'L')
    pdf.ln(5)
    
    for comp_name, comp in data['components'].items():
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 10, f"Component: {comp_name}", 0, 1, 'L')
        
        pdf.set_font('DejaVu', '', 10)
        details = [
            f"Type: {comp['type']}",
            f"Safety Level: {comp['safety_level']}",
            f"Interfaces: {', '.join(comp['interfaces'])}",
            f"Access Points: {', '.join(comp['access_points'])}",
            f"Data Types: {', '.join(comp['data_types'])}",
            f"Location: {comp['location']}",
            f"Trust Zone: {comp['trust_zone']}",
            f"Connected To: {', '.join(comp['connected_to'])}"
        ]
        for detail in details:
            pdf.cell(0, 5, detail, 0, 1, 'L')
        
        if comp.get('threats'):
            pdf.set_font('DejaVu', '', 11)
            pdf.ln(5)
            pdf.cell(0, 10, 'Identified Threats:', 0, 1, 'L')
            
            for threat in comp['threats']:
                pdf.set_font('DejaVu', '', 10)
                pdf.cell(0, 5, f"- {threat['name']}", 0, 1, 'L')
                
                impact = [
                    f"Impact Scores: {threat['impact_scores']}",
                    f"Risk Scores: {threat['risk_scores']}",
                    f"Risk Factors: {', '.join(f'{k}: {v:.2f}' for k, v in threat['risk_factors'].items())}"
                ]
                for detail in impact:
                    pdf.cell(0, 5, '  ' + detail, 0, 1, 'L')
                
                if 'description' in threat:
                    desc = threat['description'][:200]
                    pdf.multi_cell(0, 5, f"  Description: {desc}...")
                
                if 'attack_chains' in threat:
                    pdf.cell(0, 5, '  Attack Chains:', 0, 1, 'L')
                    for chain in threat['attack_chains']:
                        pdf.cell(0, 5, f"  * {' -> '.join(chain['chain'])}", 0, 1, 'L')
                        pdf.cell(0, 5, f"    Risk: {chain['risk_scores']}", 0, 1, 'L')
                
                pdf.ln(5)
        
        pdf.ln(10)
    
    try:
        pdf.output(str(output_file))
    except UnicodeEncodeError:
        # Fallback to basic ASCII if Unicode fails
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, 'Error: Unicode characters in report', 0, 1, 'C')
        pdf.cell(0, 10, 'Please view JSON or Excel output instead', 0, 1, 'C')
        pdf.output(str(output_file))

def export_report(data: Dict, output_file: Path, format: str) -> None:
    """Export report data to specified format"""
    if format == 'json':
        export_to_json(data, output_file.with_suffix('.json'))
    elif format == 'excel':
        export_to_excel(data, output_file.with_suffix('.xlsx'))
    elif format == 'pdf':
        export_to_pdf(data, output_file.with_suffix('.pdf'))
