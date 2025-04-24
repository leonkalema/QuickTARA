"""
Export formats module for QuickTARA
Handles export to JSON, Excel, and PDF formats
"""

import json
from pathlib import Path
from typing import Dict
import pandas as pd

def export_to_json(data: Dict, output_file: Path) -> None:
    """Export report data to JSON format"""
    with output_file.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def export_to_excel(data: Dict, output_file: Path) -> None:
    """Export report data to Excel format with multiple sheets"""
    try:
        # Create Excel writer
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Components overview sheet
            components_data = []
            for name, comp in data['components'].items():
                if not isinstance(comp, dict):
                    continue
                    
                comp_row = {
                    'Name': name,
                    'Type': comp.get('type', 'Unknown'),
                    'Safety Level': comp.get('safety_level', 'Unknown'),
                    'Interfaces': '|'.join(comp.get('interfaces', [])),
                    'Access Points': '|'.join(comp.get('access_points', [])),
                    'Data Types': '|'.join(comp.get('data_types', [])),
                    'Location': comp.get('location', 'Unknown'),
                    'Trust Zone': comp.get('trust_zone', 'Unknown'),
                    'Connected To': '|'.join(comp.get('connected_to', []))
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
                        'Description': threat.get('description', '')[:200],
                        'Likelihood': threat.get('likelihood', 0)
                    }
                    
                    # Add impact scores
                    impact = threat.get('impact', {})
                    for category, score in impact.items():
                        threat_row[f'Impact: {category}'] = score
                    
                    # Add risk factors
                    risk_factors = threat.get('risk_factors', {})
                    for factor, value in risk_factors.items():
                        threat_row[f'Risk Factor: {factor}'] = value
                        
                    threats_data.append(threat_row)
            
            if threats_data:
                pd.DataFrame(threats_data).to_excel(writer, sheet_name='Threats', index=False)
            
            # STRIDE Analysis sheet
            stride_data = []
            for comp_name, comp in data['components'].items():
                if 'stride_analysis' in comp:
                    for category, details in comp.get('stride_analysis', {}).items():
                        stride_row = {
                            'Component': comp_name,
                            'Category': category,
                            'Risk Level': details.get('risk_level', 'Low')
                        }
                        
                        # Add recommendations
                        recommendations = details.get('recommendations', [])
                        for i, rec in enumerate(recommendations, 1):
                            if i <= 3:  # Limit to 3 recommendations per row
                                stride_row[f'Recommendation {i}'] = rec
                        
                        stride_data.append(stride_row)
            
            if stride_data:
                pd.DataFrame(stride_data).to_excel(writer, sheet_name='STRIDE Analysis', index=False)
                
            # Attack Paths sheet
            paths_data = []
            for comp_name, comp in data['components'].items():
                if 'attack_paths' in comp:
                    for path_info in comp.get('attack_paths', []):
                        path = path_info.get('path', [])
                        risk = path_info.get('risk', {})
                        
                        path_row = {
                            'Component': comp_name,
                            'Path': ' -> '.join(path),
                            'Path Length': len(path)
                        }
                        
                        # Add risk scores
                        for category, score in risk.items():
                            path_row[f'Risk: {category}'] = score
                        
                        paths_data.append(path_row)
            
            if paths_data:
                pd.DataFrame(paths_data).to_excel(writer, sheet_name='Attack Paths', index=False)
                
            # Risk Acceptance sheet
            risk_data = []
            for comp_name, comp in data['components'].items():
                if 'risk_acceptance' in comp:
                    for threat_name, assessment in comp.get('risk_acceptance', {}).items():
                        risk_row = {
                            'Component': comp_name,
                            'Threat': threat_name,
                            'Severity': assessment.get('risk_severity', 'Medium'),
                            'Decision': assessment.get('decision', 'Mitigate'),
                            'Residual Risk': assessment.get('residual_risk', 0.5),
                            'Justification': assessment.get('justification', '')[:200]
                        }
                        
                        # Add conditions
                        conditions = assessment.get('conditions', [])
                        for i, condition in enumerate(conditions, 1):
                            if i <= 3:  # Limit to 3 conditions per row
                                risk_row[f'Condition {i}'] = condition
                        
                        risk_data.append(risk_row)
            
            if risk_data:
                pd.DataFrame(risk_data).to_excel(writer, sheet_name='Risk Acceptance', index=False)
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        # Fallback to JSON if Excel export fails
        export_to_json(data, output_file.with_suffix('.json'))

def export_to_text(data: Dict, output_file: Path) -> None:
    """Export report data to plain text format"""
    with output_file.open('w', encoding='utf-8') as f:
        # Report header
        f.write("==== QuickTARA Security Analysis Report ====\n\n")
        f.write(f"Generated: {data.get('generated_at', '')}\n\n")
        
        # Summary section
        summary = data.get('summary', {})
        f.write("=== Summary ===\n")
        f.write(f"Total Components: {summary.get('total_components', 0)}\n")
        f.write(f"Total Threats: {summary.get('total_threats', 0)}\n")
        f.write(f"Critical Components: {summary.get('critical_components', 0)}\n")
        f.write(f"High Risk Threats: {summary.get('high_risk_threats', 0)}\n\n")
        
        # Components section
        f.write("=== Components ===\n\n")
        for comp_id, comp in data.get('components', {}).items():
            if not isinstance(comp, dict):
                continue
                
            f.write(f"Component: {comp_id} - {comp.get('name', '')}\n")
            f.write(f"Type: {comp.get('type', 'Unknown')}\n")
            f.write(f"Safety Level: {comp.get('safety_level', 'Unknown')}\n")
            f.write(f"Interfaces: {', '.join(comp.get('interfaces', []))}\n")
            f.write(f"Access Points: {', '.join(comp.get('access_points', []))}\n")
            f.write(f"Data Types: {', '.join(comp.get('data_types', []))}\n")
            f.write(f"Location: {comp.get('location', 'Unknown')}\n")
            f.write(f"Trust Zone: {comp.get('trust_zone', 'Unknown')}\n")
            f.write(f"Connected To: {', '.join(comp.get('connected_to', []))}\n\n")
            
            # Threats
            f.write("  Threats:\n")
            for threat in comp.get('threats', []):
                f.write(f"  - {threat.get('name', '')}\n")
                f.write(f"    Description: {threat.get('description', '')[:100]}...\n")
                f.write(f"    Likelihood: {threat.get('likelihood', 0)}\n")
                
                # Impact
                impact = threat.get('impact', {})
                f.write("    Impact:\n")
                for category, score in impact.items():
                    f.write(f"      {category}: {score}\n")
                
                # Risk factors
                risk_factors = threat.get('risk_factors', {})
                f.write("    Risk Factors:\n")
                for factor, value in risk_factors.items():
                    f.write(f"      {factor}: {value:.2f}\n")
                
                f.write("\n")
            
            # STRIDE Analysis
            if 'stride_analysis' in comp:
                f.write("  STRIDE Analysis:\n")
                for category, details in comp.get('stride_analysis', {}).items():
                    f.write(f"  - {category}: {details.get('risk_level', 'Low')}\n")
                    if 'recommendations' in details:
                        f.write("    Recommendations:\n")
                        for rec in details.get('recommendations', []):
                            f.write(f"      * {rec}\n")
                f.write("\n")
            
            # Attack Paths
            if 'attack_paths' in comp:
                f.write("  Attack Paths:\n")
                for path_info in comp.get('attack_paths', []):
                    path = path_info.get('path', [])
                    risk = path_info.get('risk', {})
                    
                    f.write(f"  - Path: {' -> '.join(path)}\n")
                    f.write("    Risk Scores:\n")
                    for category, score in risk.items():
                        f.write(f"      {category}: {score}\n")
                f.write("\n")
            
            # Risk Acceptance
            if 'risk_acceptance' in comp:
                f.write("  Risk Acceptance:\n")
                for threat_name, assessment in comp.get('risk_acceptance', {}).items():
                    f.write(f"  - Threat: {threat_name}\n")
                    f.write(f"    Severity: {assessment.get('risk_severity', 'Medium')}\n")
                    f.write(f"    Decision: {assessment.get('decision', 'Mitigate')}\n")
                    f.write(f"    Residual Risk: {assessment.get('residual_risk', 0.5):.1%}\n")
                    f.write(f"    Justification: {assessment.get('justification', '')}\n")
                    
                    if 'conditions' in assessment:
                        f.write("    Conditions:\n")
                        for condition in assessment.get('conditions', []):
                            f.write(f"      * {condition}\n")
                    
                    f.write("\n")
            
            f.write("\n")

def export_report(data: Dict, output_path: Path, format: str = 'txt') -> None:
    """Export report data to specified format"""
    if format == 'json':
        export_to_json(data, output_path.with_suffix('.json'))
    elif format == 'xlsx':
        export_to_excel(data, output_path.with_suffix('.xlsx'))
    elif format == 'pdf':
        # Attempt to use export_to_pdf from the main module if available
        try:
            from export_formats import export_to_pdf
            export_to_pdf(data, output_path.with_suffix('.pdf'))
        except ImportError:
            print("PDF export not available in core module; falling back to text format")
            export_to_text(data, output_path.with_suffix('.txt'))
    else:  # Default to text
        export_to_text(data, output_path.with_suffix('.txt'))
