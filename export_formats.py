"""
Export formats module for QuickTARA
Handles export to JSON, Excel, and PDF formats
"""

import json
from pathlib import Path
from typing import Dict
import pandas as pd
from fpdf import FPDF
from cybersecurity_goals import format_goal_mappings
from attacker_feasibility import format_feasibility_assessment
from risk_acceptance import format_risk_acceptance
from risk_review import format_review_decision

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
        
        # Cybersecurity Goals sheet
        goals_data = []
        for comp_name, comp in data['components'].items():
            if isinstance(comp, dict) and 'cybersecurity_goals' in comp:
                for threat_name, mappings in comp.get('cybersecurity_goals', {}).items():
                    # Check if mappings is a list or dictionary
                    if isinstance(mappings, list):
                        for mapping in mappings:
                            if isinstance(mapping, dict):
                                goals_row = {
                                    'Component': comp_name,
                                    'Threat': threat_name,
                                    'Goal': mapping.get('goal', 'Unknown'),
                                    'Relevance': mapping.get('relevance', 0),
                                    'Description': mapping.get('description', ''),
                                    'Requirements': '\n'.join(mapping.get('requirements', [])[:3]) if 'requirements' in mapping else ''
                                }
                                goals_data.append(goals_row)
                    else:
                        # Handle non-list case (could be object representation in memory)
                        try:
                            goals_row = {
                                'Component': comp_name,
                                'Threat': threat_name,
                                'Goal': str(mappings),
                                'Relevance': 0,
                                'Description': '',
                                'Requirements': ''
                            }
                            goals_data.append(goals_row)
                        except Exception as e:
                            print(f"Error processing goal mapping: {e}")
        
        if goals_data:
            pd.DataFrame(goals_data).to_excel(writer, sheet_name='Cybersecurity Goals', index=False)
        
        # Feasibility Assessments sheet
        feasibility_data = []
        for comp_name, comp in data['components'].items():
            if 'feasibility_assessments' in comp:
                for threat_name, assessment in comp.get('feasibility_assessments', {}).items():
                    # Get overall assessment
                    overall = assessment.get('feasibility_level', 'Medium')
                    score = assessment.get('overall_score', 3)
                    
                    # Get top attacker profile
                    profiles = assessment.get('profiles', {})
                    top_profile = max(profiles.items(), key=lambda x: x[1])[0] if profiles else 'Unknown'
                    
                    # Create row
                    feasibility_row = {
                        'Component': comp_name,
                        'Threat': threat_name,
                        'Feasibility Level': overall,
                        'Score': score,
                        'Technical Capability': assessment.get('technical_capability', 3),
                        'Knowledge Required': assessment.get('knowledge_required', 3),
                        'Resources Needed': assessment.get('resources_needed', 3),
                        'Time Required': assessment.get('time_required', 3),
                        'Top Attacker Profile': top_profile,
                        'Enabling Factors': '\n'.join(assessment.get('enabling_factors', [])),
                        'Mitigating Factors': '\n'.join(assessment.get('mitigating_factors', []))
                    }
                    feasibility_data.append(feasibility_row)
        
        if feasibility_data:
            pd.DataFrame(feasibility_data).to_excel(writer, sheet_name='Attacker Feasibility', index=False)
            
        # Risk Acceptance Criteria sheet
        risk_acceptance_data = []
        for comp_name, comp in data['components'].items():
            if 'risk_acceptance' in comp:
                for threat_name, assessment in comp.get('risk_acceptance', {}).items():
                    # Create row
                    risk_row = {
                        'Component': comp_name,
                        'Threat': threat_name,
                        'Risk Severity': assessment.get('risk_severity', 'Medium'),
                        'Decision': assessment.get('decision', 'Mitigate'),
                        'Residual Risk': assessment.get('residual_risk', 0.5),
                        'Justification': assessment.get('justification', ''),
                        'Reassessment Period': assessment.get('criteria', {}).get('reassessment_period', 12),
                        'Conditions': '\n'.join(assessment.get('conditions', [])[:3]),
                        'Required Approvals': '\n'.join(assessment.get('approvers', []))
                    }
                    risk_acceptance_data.append(risk_row)
        
        if risk_acceptance_data:
            pd.DataFrame(risk_acceptance_data).to_excel(writer, sheet_name='Risk Acceptance', index=False)
            
        # Risk Treatment Reviews sheet
        risk_reviews_data = []
        for comp_name, comp in data['components'].items():
            if 'risk_acceptance' in comp:
                for threat_name, assessment in comp.get('risk_acceptance', {}).items():
                    # Check if review data exists
                    review_status = 'Not Reviewed'
                    reviewer = ''
                    review_date = ''
                    final_decision = assessment.get('decision', '')
                    original_decision = ''
                    justification = assessment.get('justification', '')
                    evidence = ''
                    
                    if 'reviewer' in assessment:
                        review_status = 'Reviewed'
                        reviewer = assessment.get('reviewer', '')
                        review_date = assessment.get('review_date', '')
                        original_decision = assessment.get('original_decision', final_decision)
                        justification = assessment.get('justification', '')
                        evidence = '\n'.join(assessment.get('evidence_references', []))
                    
                    # Create row
                    review_row = {
                        'Component': comp_name,
                        'Threat': threat_name,
                        'Review Status': review_status,
                        'Original Decision': original_decision,
                        'Final Decision': final_decision,
                        'Reviewer': reviewer,
                        'Review Date': review_date,
                        'Justification': justification,
                        'Evidence References': evidence
                    }
                    risk_reviews_data.append(review_row)
        
        if risk_reviews_data:
            pd.DataFrame(risk_reviews_data).to_excel(writer, sheet_name='Risk Treatment Reviews', index=False)

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
        # Skip non-dictionary components
        if not isinstance(comp, dict):
            continue
            
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 10, f"Component: {comp_name}", 0, 1, 'L')
        
        pdf.set_font('DejaVu', '', 10)
        details = [
            f"Type: {comp.get('type', 'Unknown')}",
            f"Safety Level: {comp.get('safety_level', 'Unknown')}",
            f"Interfaces: {', '.join(comp.get('interfaces', []))}",
            f"Access Points: {', '.join(comp.get('access_points', []))}",
            f"Data Types: {', '.join(comp.get('data_types', []))}",
            f"Location: {comp.get('location', 'Unknown')}",
            f"Trust Zone: {comp.get('trust_zone', 'Unknown')}",
            f"Connected To: {', '.join(comp.get('connected_to', []))}"
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
        
        # Cybersecurity Goals section
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 10, 'Cybersecurity Goals', 0, 1, 'L')
        pdf.ln(5)
        
        for comp_name, comp in data['components'].items():
            if isinstance(comp, dict) and 'cybersecurity_goals' in comp and comp['cybersecurity_goals']:
                pdf.set_font('DejaVu', '', 12)
                pdf.cell(0, 10, f"Component: {comp_name}", 0, 1, 'L')
                
                for threat_name, mappings in comp['cybersecurity_goals'].items():
                    pdf.set_font('DejaVu', '', 11)
                    pdf.cell(0, 5, f"Threat: {threat_name}", 0, 1, 'L')
                    
                    # Handle both list and object formats
                    if isinstance(mappings, list):
                        for mapping in mappings:
                            if isinstance(mapping, dict):
                                pdf.set_font('DejaVu', '', 10)
                                pdf.cell(0, 5, f"Goal: {mapping.get('goal', 'Unknown')} (Relevance: {mapping.get('relevance', 0)}/5)", 0, 1, 'L')
                                pdf.multi_cell(0, 5, f"Description: {mapping.get('description', '')}")
                                pdf.cell(0, 5, "Requirements:", 0, 1, 'L')
                                
                                requirements = mapping.get('requirements', [])
                                if isinstance(requirements, list):
                                    for req in requirements[:3]:  # Top 3 requirements
                                        pdf.cell(0, 5, f"- {req}", 0, 1, 'L')
                                
                                pdf.ln(5)
                    else:
                        # Handle non-list format
                        try:
                            pdf.set_font('DejaVu', '', 10)
                            pdf.cell(0, 5, f"Goal: {str(mappings)}", 0, 1, 'L')
                            pdf.ln(5)
                        except Exception as e:
                            pdf.cell(0, 5, f"Error processing goal: {str(e)}", 0, 1, 'L')
                
                pdf.ln(5)
        
        # Attacker Feasibility section
        if any('feasibility_assessments' in comp for comp in data['components'].values()):
            pdf.set_font('DejaVu', '', 14)
            pdf.cell(0, 10, 'Attacker Feasibility Assessments', 0, 1, 'L')
            pdf.ln(5)
            
            for comp_name, comp in data['components'].items():
                if 'feasibility_assessments' in comp and comp['feasibility_assessments']:
                    pdf.set_font('DejaVu', '', 12)
                    pdf.cell(0, 10, f"Component: {comp_name}", 0, 1, 'L')
                    
                    for threat_name, assessment in comp['feasibility_assessments'].items():
                        pdf.set_font('DejaVu', '', 11)
                        pdf.cell(0, 5, f"Threat: {threat_name}", 0, 1, 'L')
                        
                        pdf.set_font('DejaVu', '', 10)
                        pdf.cell(0, 5, f"Feasibility Level: {assessment.get('feasibility_level', 'Medium')} ({assessment.get('overall_score', 3)}/5)", 0, 1, 'L')
                        
                        # Key factors
                        pdf.cell(0, 5, "Attack Difficulty Factors:", 0, 1, 'L')
                        pdf.cell(0, 5, f"- Technical Capability: {assessment.get('technical_capability', 3)}/5", 0, 1, 'L')
                        pdf.cell(0, 5, f"- Knowledge Required: {assessment.get('knowledge_required', 3)}/5", 0, 1, 'L')
                        pdf.cell(0, 5, f"- Resources Needed: {assessment.get('resources_needed', 3)}/5", 0, 1, 'L')
                        pdf.cell(0, 5, f"- Time Required: {assessment.get('time_required', 3)}/5", 0, 1, 'L')
                        
                        # Attacker profiles
                        if 'profiles' in assessment:
                            profiles = assessment['profiles']
                            pdf.cell(0, 5, "Relevant Attacker Profiles:", 0, 1, 'L')
                            for profile, score in sorted(profiles.items(), key=lambda x: x[1], reverse=True)[:2]:
                                pdf.cell(0, 5, f"- {profile}: {score}/5 relevance", 0, 1, 'L')
                        
                        # Factors
                        if 'enabling_factors' in assessment and assessment['enabling_factors']:
                            pdf.cell(0, 5, "Enabling Factors:", 0, 1, 'L')
                            for factor in assessment['enabling_factors']:
                                pdf.cell(0, 5, f"- {factor}", 0, 1, 'L')
                        
                        if 'mitigating_factors' in assessment and assessment['mitigating_factors']:
                            pdf.cell(0, 5, "Mitigating Factors:", 0, 1, 'L')
                            for factor in assessment['mitigating_factors']:
                                pdf.cell(0, 5, f"- {factor}", 0, 1, 'L')
                                
                        pdf.ln(5)
                        
                        pdf.ln(5)
                                
        # Risk Acceptance section
        if any('risk_acceptance' in comp for comp in data['components'].values()):
            pdf.set_font('DejaVu', '', 14)
            pdf.cell(0, 10, 'Risk Acceptance Criteria (Clause 14)', 0, 1, 'L')
            pdf.ln(5)
            
            for comp_name, comp in data['components'].items():
                if 'risk_acceptance' in comp and comp['risk_acceptance']:
                    pdf.set_font('DejaVu', '', 12)
                    pdf.cell(0, 10, f"Component: {comp_name}", 0, 1, 'L')
                    
                    for threat_name, assessment in comp['risk_acceptance'].items():
                        pdf.set_font('DejaVu', '', 11)
                        pdf.cell(0, 5, f"Threat: {threat_name}", 0, 1, 'L')
                        
                        pdf.set_font('DejaVu', '', 10)
                        pdf.cell(0, 5, f"Decision: {assessment.get('decision', 'Mitigate')}", 0, 1, 'L')
                        pdf.cell(0, 5, f"Risk Severity: {assessment.get('risk_severity', 'Medium')}", 0, 1, 'L')
                        pdf.cell(0, 5, f"Residual Risk: {assessment.get('residual_risk', 0.5):.1%}", 0, 1, 'L')
                        
                        # Justification
                        if 'justification' in assessment and assessment['justification']:
                            pdf.multi_cell(0, 5, f"Justification: {assessment['justification']}")
                        
                        # Conditions
                        if 'conditions' in assessment and assessment['conditions']:
                            pdf.cell(0, 5, "Conditions:", 0, 1, 'L')
                            for condition in assessment['conditions'][:3]:  # Show top 3 for readability
                                pdf.cell(0, 5, f"- {condition}", 0, 1, 'L')
                        
                        # Required approvals
                        if 'approvers' in assessment and assessment['approvers']:
                            pdf.cell(0, 5, "Required Approvals:", 0, 1, 'L')
                            for approver in assessment['approvers']:
                                pdf.cell(0, 5, f"- {approver}", 0, 1, 'L')
                        
                        # Reassessment period
                        if 'criteria' in assessment and 'reassessment_period' in assessment['criteria']:
                            period = assessment['criteria']['reassessment_period']
                            pdf.cell(0, 5, f"Reassessment Period: {period} months", 0, 1, 'L')
                        
                        pdf.ln(5)
                    
                    pdf.ln(5)
                    
        # Risk Treatment Review section
        if any('review_status' in comp.get('risk_acceptance', {}).get(threat_name, {}) 
               for comp in data['components'].values() 
               for threat_name in comp.get('risk_acceptance', {})):
            pdf.set_font('DejaVu', '', 14)
            pdf.cell(0, 10, 'Risk Treatment Reviews', 0, 1, 'L')
            pdf.ln(5)
            
            for comp_name, comp in data['components'].items():
                if 'risk_acceptance' in comp:
                    has_reviews = any('reviewer' in assessment for assessment in comp['risk_acceptance'].values())
                    if has_reviews:
                        pdf.set_font('DejaVu', '', 12)
                        pdf.cell(0, 10, f"Component: {comp_name}", 0, 1, 'L')
                        
                        for threat_name, assessment in comp['risk_acceptance'].items():
                            if 'reviewer' in assessment:
                                pdf.set_font('DejaVu', '', 11)
                                pdf.cell(0, 5, f"Threat: {threat_name}", 0, 1, 'L')
                                
                                pdf.set_font('DejaVu', '', 10)
                                final_decision = assessment.get('decision', 'Mitigate')
                                original_decision = assessment.get('original_decision', final_decision)
                                
                                pdf.cell(0, 5, f"Review Status: Reviewed", 0, 1, 'L')
                                pdf.cell(0, 5, f"Final Decision: {final_decision}", 0, 1, 'L')
                                
                                if original_decision != final_decision:
                                    pdf.cell(0, 5, f"Original Decision: {original_decision}", 0, 1, 'L')
                                
                                pdf.cell(0, 5, f"Reviewer: {assessment.get('reviewer', '')}", 0, 1, 'L')
                                pdf.cell(0, 5, f"Review Date: {assessment.get('review_date', '')}", 0, 1, 'L')
                                
                                # Justification
                                pdf.multi_cell(0, 5, f"Justification: {assessment.get('justification', '')}")
                                
                                # Additional notes
                                if 'additional_notes' in assessment and assessment['additional_notes']:
                                    pdf.multi_cell(0, 5, f"Additional Notes: {assessment['additional_notes']}")
                                
                                # Evidence references
                                if 'evidence_references' in assessment and assessment['evidence_references']:
                                    pdf.cell(0, 5, "Evidence References:", 0, 1, 'L')
                                    for evidence in assessment['evidence_references']:
                                        pdf.cell(0, 5, f"- {evidence}", 0, 1, 'L')
                                
                                pdf.ln(5)
                        
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
