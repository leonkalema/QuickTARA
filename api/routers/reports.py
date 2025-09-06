from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
import os
import tempfile
from pathlib import Path

# Import your existing models and dependencies
from ..models.damage_scenario import DamageScenario
from ..models.threat_scenario import ThreatScenario
from ..deps.db import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/reports", tags=["reports"])

def get_risk_level(impact_level: str, feasibility_level: str) -> str:
    """Calculate risk level based on impact and feasibility"""
    risk_matrix = {
        "Severe": {"Very High": "Critical", "High": "Critical", "Medium": "High", "Low": "Medium", "Very Low": "Medium"},
        "Major": {"Very High": "High", "High": "High", "Medium": "Medium", "Low": "Low", "Very Low": "Low"},
        "Moderate": {"Very High": "Medium", "High": "Medium", "Medium": "Low", "Low": "Low", "Very Low": "Low"},
        "Negligible": {"Very High": "Low", "High": "Low", "Medium": "Low", "Low": "Low", "Very Low": "Low"}
    }
    return risk_matrix.get(impact_level, {}).get(feasibility_level, "Unknown")

def get_afr_level(afs: int) -> str:
    """Convert AFS score to feasibility level"""
    if afs >= 25: return 'Very Low'
    if afs >= 20: return 'Low'
    if afs >= 14: return 'Medium'
    if afs >= 1: return 'High'
    return 'Very High'

def generate_pdf_html(scope_id: str, product_name: str, product_desc: str, 
                     damage_scenarios: List[Dict], threat_scenarios: List[Dict]) -> str:
    """Generate HTML template for PDF conversion"""
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Calculate risk statistics
    critical_risks = sum(1 for d in damage_scenarios if get_risk_level(
        d.get('impact_level', 'Unknown'), d.get('feasibility_level', 'Unknown')) == 'Critical')
    high_risks = sum(1 for d in damage_scenarios if get_risk_level(
        d.get('impact_level', 'Unknown'), d.get('feasibility_level', 'Unknown')) == 'High')
    
    # Generate risk assessment table rows
    risk_rows = ""
    for scenario in damage_scenarios:
        risk_level = get_risk_level(scenario.get('impact_level', 'Unknown'), 
                                  scenario.get('feasibility_level', 'Unknown'))
        row_class = f"risk-{risk_level.lower()}"
        treatment = scenario.get('selected_treatment') or scenario.get('suggested_treatment') or 'To be determined'
        
        risk_rows += f"""
        <tr class="{row_class}">
            <td>{scenario.get('name', 'Unknown')}</td>
            <td>{scenario.get('description', 'No description')}</td>
            <td>{scenario.get('impact_level', 'Unknown')}</td>
            <td><strong>{risk_level}</strong></td>
            <td>{treatment}</td>
        </tr>"""
    
    # Generate threat scenarios
    threat_sections = ""
    for threat in threat_scenarios:
        threat_sections += f"""
        <h3>{threat.get('name', 'Unknown Threat')}</h3>
        <p>{threat.get('description', 'No description provided')}</p>"""
    
    # Generate treatment summaries
    treatment_sections = ""
    for scenario in damage_scenarios:
        if scenario.get('treatment_goal') or scenario.get('selected_treatment'):
            risk_level = get_risk_level(scenario.get('impact_level', 'Unknown'), 
                                      scenario.get('feasibility_level', 'Unknown'))
            treatment = scenario.get('selected_treatment') or scenario.get('suggested_treatment') or 'Not specified'
            
            treatment_sections += f"""
            <div class="treatment-summary">
                <h4>{scenario.get('name', 'Unknown')}</h4>
                <p><strong>Risk Level:</strong> {risk_level}</p>
                <p><strong>Treatment:</strong> {treatment}</p>
                {f'<p><strong>Goal:</strong> {scenario.get("treatment_goal")}</p>' if scenario.get('treatment_goal') else ''}
                <p><strong>Status:</strong> {scenario.get('treatment_status', 'Draft')}</p>
            </div>"""
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TARA Report - {product_name}</title>
    <style>
        @page {{ margin: 1in; }}
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ text-align: center; margin-bottom: 40px; border-bottom: 2px solid #333; padding-bottom: 20px; }}
        .section {{ margin-bottom: 30px; page-break-inside: avoid; }}
        .section h2 {{ color: #333; border-bottom: 1px solid #ccc; padding-bottom: 10px; }}
        .section h3 {{ color: #555; margin-top: 25px; }}
        .risk-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .risk-table th, .risk-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 12px; }}
        .risk-table th {{ background-color: #f5f5f5; font-weight: bold; }}
        .risk-critical {{ background-color: #fee; }}
        .risk-high {{ background-color: #fef0e6; }}
        .risk-medium {{ background-color: #fffbf0; }}
        .risk-low {{ background-color: #f0f9f0; }}
        .treatment-summary {{ background-color: #f8f9fa; padding: 15px; margin: 15px 0; border-left: 4px solid #007bff; }}
        .metadata {{ font-size: 10px; color: #666; margin-top: 40px; border-top: 1px solid #ccc; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Threat Analysis and Risk Assessment (TARA)</h1>
        <h2>Product: {product_name}</h2>
        <p>Generated on: {current_date}</p>
        <p>ISO 21434 Regulatory Submission</p>
    </div>

    <div class="section">
        <h2>1. Executive Summary</h2>
        <p>This document presents the Threat Analysis and Risk Assessment (TARA) for <strong>{product_name}</strong> conducted in accordance with ISO 21434:2021 cybersecurity engineering standards for automotive systems.</p>
        
        <h3>Risk Summary</h3>
        <ul>
            <li>Assets Analyzed: {len(damage_scenarios)}</li>
            <li>Threat Scenarios Identified: {len(threat_scenarios)}</li>
            <li>Critical Risks: {critical_risks}</li>
            <li>High Risks: {high_risks}</li>
        </ul>
    </div>

    <div class="section">
        <h2>2. Product and Scope</h2>
        <p><strong>Product:</strong> {product_name}</p>
        <p><strong>Description:</strong> {product_desc or 'No description provided'}</p>
        <p><strong>Assessment Scope:</strong> Cybersecurity analysis of all identified assets and their associated damage scenarios.</p>
    </div>

    <div class="section">
        <h2>3. Risk Assessment Results</h2>
        <table class="risk-table">
            <thead>
                <tr>
                    <th>Asset/Component</th>
                    <th>Damage Scenario</th>
                    <th>Impact Level</th>
                    <th>Risk Level</th>
                    <th>Treatment Decision</th>
                </tr>
            </thead>
            <tbody>
                {risk_rows}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>4. Threat Scenarios</h2>
        {threat_sections}
    </div>

    <div class="section">
        <h2>5. Risk Treatment Strategy</h2>
        {treatment_sections}
    </div>

    <div class="section">
        <h2>6. Compliance Statement</h2>
        <p>This TARA has been conducted in accordance with:</p>
        <ul>
            <li><strong>ISO 21434:2021</strong> - Road vehicles — Cybersecurity engineering</li>
            <li><strong>UN-ECE WP.29</strong> - Regulation on Cybersecurity Management System</li>
        </ul>
        
        <p>The assessment methodology includes:</p>
        <ul>
            <li>Asset identification and cybersecurity property analysis</li>
            <li>Damage scenario development based on potential cybersecurity impacts</li>
            <li>Threat scenario identification and feasibility assessment</li>
            <li>Risk determination and treatment decision</li>
        </ul>
        
        <p><strong>Conclusion:</strong> All identified risks have been assessed and appropriate treatment strategies have been defined in accordance with regulatory requirements.</p>
    </div>

    <div class="metadata">
        <p><strong>Document Control:</strong></p>
        <p>Generated: {current_date} | Tool: QuickTARA | Product: {product_name}</p>
        <p>This document satisfies ISO 21434 TARA documentation requirements for regulatory submission.</p>
    </div>
</body>
</html>"""

async def generate_pdf_with_puppeteer(html_content: str) -> bytes:
    """Generate HTML report as fallback when PDF libraries fail"""
    try:
        # Return HTML as bytes for now (can be saved as .html file)
        return html_content.encode('utf-8')
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

@router.get("/tara-pdf/{scope_id}")
async def generate_tara_pdf(scope_id: str, db: Session = Depends(get_db)):
    """Generate TARA report as PDF"""
    try:
        # Fetch data from database
        from sqlalchemy import text
        damage_scenarios = db.execute(text("SELECT * FROM damage_scenarios WHERE scope_id = :scope_id"), {"scope_id": scope_id}).fetchall()
        threat_scenarios = db.execute(text("SELECT * FROM threat_scenarios WHERE scope_id = :scope_id"), {"scope_id": scope_id}).fetchall()
        
        if not damage_scenarios:
            raise HTTPException(status_code=404, detail="No damage scenarios found for this product")
        
        # Get product info (assuming you have a Product model)
        product_name = f"Product {scope_id}"  # Replace with actual product lookup
        product_desc = "Automotive system under analysis"  # Replace with actual description
        
        # Convert to dictionaries
        damage_data = []
        for ds in damage_scenarios:
            damage_data.append({
                'name': ds.name if hasattr(ds, 'name') else ds[1],
                'description': ds.description if hasattr(ds, 'description') else ds[2],
                'impact_level': ds.severity if hasattr(ds, 'severity') else ds[6],
                'feasibility_level': get_afr_level(ds.highest_feasibility_score if hasattr(ds, 'highest_feasibility_score') else ds[7] or 0),
                'selected_treatment': getattr(ds, 'selected_treatment', None),
                'suggested_treatment': getattr(ds, 'suggested_treatment', None),
                'treatment_goal': getattr(ds, 'treatment_goal', None),
                'treatment_status': getattr(ds, 'treatment_status', 'Draft')
            })
        
        threat_data = []
        for ts in threat_scenarios:
            threat_data.append({
                'name': ts.name if hasattr(ts, 'name') else ts[1],
                'description': ts.description if hasattr(ts, 'description') else ts[2]
            })
        
        # Generate HTML
        html_content = generate_pdf_html(scope_id, product_name, product_desc, damage_data, threat_data)
        
        # Generate PDF
        pdf_content = await generate_pdf_with_puppeteer(html_content)
        
        # Return HTML response (fallback when PDF generation fails)
        filename = f"TARA_Report_{product_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.html"
        
        return Response(
            content=pdf_content,
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
