#!/usr/bin/env python3
"""
QuickTARA CLI
A command-line interface for automotive threat analysis and risk assessment
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
import click
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# Import core QuickTARA functionality
from quicktara import load_components, analyze_threats, write_report

console = Console()

def display_components(components: Dict):
    """Display components in a formatted table"""
    table = Table(title="Components")
    
    # Add columns
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green", no_wrap=True)
    table.add_column("Type", style="magenta", no_wrap=True)
    table.add_column("Safety", style="red", no_wrap=True)
    table.add_column("Location", style="blue", no_wrap=True)
    table.add_column("Trust Zone", style="yellow", no_wrap=True)
    
    # Add rows
    for comp_id, comp in components.items():
        if isinstance(comp, dict):
            table.add_row(
                comp_id,
                comp['name'],
                comp['type'],
                comp['safety_level'],
                comp['location'],
                comp['trust_zone']
            )
        else:
            table.add_row(
                comp_id,
                comp.name,
                comp.type.value,
                comp.safety_level.value,
                comp.location,
                comp.trust_zone.value
            )
    
    console.print(table)

def analyze(asset_file: str):
    """Analyze threats for components in the asset file"""
    console = Console()
    
    try:
        # Load and display components
        components = load_components(Path(asset_file))
        display_components(components)
        
        # Analyze threats
        console.print("\n[bold green]Analyzing threats...[/bold green]")
        analyzed = analyze_threats(components)
        
        # Display threats with proper impact scores
        console.print("\n[bold red]Identified Threats:[/bold red]")
        table = Table(title="Identified Threats")
        table.add_column("Component", style="cyan", no_wrap=True)
        table.add_column("Threat", style="red", no_wrap=True)
        table.add_column("Impact", style="yellow")
        table.add_column("Risk Level", style="magenta")
        
        for comp_id, comp in analyzed.items():
            for threat in comp.get('threats', []):
                impact = threat.get('impact', {})
                impact_str = (
                    f"Financial: {impact.get('financial', 0)}\n"
                    f"Safety: {impact.get('safety', 0)}\n"
                    f"Privacy: {impact.get('privacy', 0)}"
                )
                
                risk_factors = threat.get('risk_factors', {})
                risk_level = (
                    risk_factors.get('exposure', 0) * 
                    risk_factors.get('complexity', 0) * 
                    risk_factors.get('attack_surface', 0)
                )
                risk_str = f"Overall: {risk_level:.2f}"
                
                table.add_row(
                    comp['name'],
                    threat['name'],
                    impact_str,
                    risk_str
                )
        
        console.print(table)
        
        # Display STRIDE analysis
        console.print("\n[bold yellow]STRIDE Analysis:[/bold yellow]")
        stride_table = Table(title="STRIDE Analysis")
        stride_table.add_column("Component", style="cyan", no_wrap=True)
        stride_table.add_column("Category", style="red", no_wrap=True)
        stride_table.add_column("Risk Level", style="yellow", no_wrap=True)
        stride_table.add_column("Recommendations", style="magenta")
        
        for comp_id, comp in analyzed.items():
            stride = comp.get('stride_analysis', {})
            for category, details in stride.items():
                stride_table.add_row(
                    comp['name'],
                    category,
                    details['risk_level'],
                    "\n".join(details.get('recommendations', []))
                )
        
        console.print(stride_table)
        
        # Display compliance requirements
        console.print("\n[bold blue]Compliance Requirements:[/bold blue]")
        compliance_table = Table(title="Compliance Requirements")
        compliance_table.add_column("Component", style="cyan", no_wrap=True)
        compliance_table.add_column("Standard", style="red", no_wrap=True)
        compliance_table.add_column("Requirement", style="yellow", no_wrap=True)
        compliance_table.add_column("Description", style="magenta")
        
        for comp_id, comp in analyzed.items():
            for req in comp.get('compliance', []):
                compliance_table.add_row(
                    comp['name'],
                    req['standard'],
                    req['requirement'],
                    req['description']
                )
        
        console.print(compliance_table)
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        raise

@click.group()
def cli():
    """QuickTARA - Automotive Security Analysis Tool"""
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', default='report', help='Output file name (without extension)')
@click.option('--format', '-f', default='txt', type=click.Choice(['txt', 'json', 'xlsx']), help='Output format')
def analyze(input_file: str, output: str, format: str):
    """Analyze components from CSV file"""
    try:
        # Load and analyze components
        components = load_components(Path(input_file))
        analyzed = analyze_threats(components)
        
        # Generate report
        output_path = Path(f"{output}.{format}")
        write_report(components, analyzed, output_path)
        
        console = Console()
        console.print(f"\n[bold green]Report saved to {output_path}[/bold green]")
        
    except Exception as e:
        console = Console()
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        raise

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def preview(input_file: str):
    """Preview components from CSV file"""
    try:
        # Load and display components
        components = load_components(Path(input_file))
        console.print("\n[bold green]Component Preview:[/bold green]")
        display_components(components)
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        raise

if __name__ == '__main__':
    cli()
