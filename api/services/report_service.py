"""
Report generation service for QuickTARA
Handles report creation, generation, and management
"""
import os
import uuid
import json
import logging
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from sqlalchemy.orm import Session

# Import our models
from db.base import Report as DbReport, Analysis as DbAnalysis
from api.models.report import (
    Report, ReportCreate, ReportSummary, ReportList, 
    ReportFormat, ReportStatus, ReportType, ReportConfiguration,
    ReportError
)
from api.models.analysis import Analysis
from api.services.analysis_service import get_analysis

# Import the export functionality
# We're directly importing from the core.export_formats module
from core.export_formats import export_to_json, export_to_excel, export_to_text

logger = logging.getLogger(__name__)

class ReportService:
    """Service for managing reports"""
    
    def __init__(self, db: Session, reports_dir: str):
        """
        Initialize the report service
        
        Args:
            db: Database session
            reports_dir: Directory for storing generated reports
        """
        self.db = db
        self.reports_dir = Path(reports_dir)
        
        # Ensure reports directory exists
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def create_report(self, report_data: ReportCreate) -> Report:
        """
        Create a new report record
        
        Args:
            report_data: Report creation data
            
        Returns:
            Report object
        """
        # Validate analysis exists
        analysis = self.db.query(DbAnalysis).filter(DbAnalysis.id == report_data.analysis_id).first()
        if not analysis:
            raise ValueError(f"Analysis with ID {report_data.analysis_id} not found")
        
        # Generate a unique ID for the report
        report_id = str(uuid.uuid4())
        
        # Create default configuration if not provided
        if report_data.configuration is None:
            report_data.configuration = ReportConfiguration()
        
        # Create database record
        db_report = DbReport(
            id=report_id,
            analysis_id=report_data.analysis_id,
            name=report_data.name or f"Report {report_id[:8]}",
            description=report_data.description,
            format=report_data.format.value,
            report_type=report_data.report_type.value,
            status=ReportStatus.PENDING.value,
            configuration=report_data.configuration.dict(),
            created_at=datetime.now()
        )
        
        # Save to database
        self.db.add(db_report)
        self.db.commit()
        self.db.refresh(db_report)
        
        # Return as Pydantic model
        return self._db_report_to_model(db_report)
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """
        Get a report by ID
        
        Args:
            report_id: Report ID
            
        Returns:
            Report object or None if not found
        """
        db_report = self.db.query(DbReport).filter(DbReport.id == report_id).first()
        if not db_report:
            return None
            
        return self._db_report_to_model(db_report)
    
    def list_reports(self, 
                     skip: int = 0, 
                     limit: int = 100, 
                     analysis_id: Optional[str] = None) -> ReportList:
        """
        List reports with optional filtering
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            analysis_id: Filter by analysis ID
            
        Returns:
            List of report summaries
        """
        query = self.db.query(DbReport)
        
        # Apply filters
        if analysis_id:
            query = query.filter(DbReport.analysis_id == analysis_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        query = query.order_by(DbReport.created_at.desc()).offset(skip).limit(limit)
        
        # Convert to Pydantic models
        reports = [self._db_report_to_summary(db_report) for db_report in query.all()]
        
        return ReportList(reports=reports, total=total)
    
    def delete_report(self, report_id: str) -> bool:
        """
        Delete a report by ID
        
        Args:
            report_id: Report ID
            
        Returns:
            True if deleted, False if not found
        """
        db_report = self.db.query(DbReport).filter(DbReport.id == report_id).first()
        if not db_report:
            return False
            
        # Delete file if it exists
        if db_report.file_path:
            try:
                os.remove(db_report.file_path)
            except OSError as e:
                logger.warning(f"Failed to delete report file {db_report.file_path}: {e}")
        
        # Delete database record
        self.db.delete(db_report)
        self.db.commit()
        
        return True
    
    def generate_report(self, report_id: str, run_async: bool = True) -> Optional[Report]:
        """
        Generate a report based on analysis results
        
        Args:
            report_id: Report ID
            run_async: Whether to run generation in a background thread
            
        Returns:
            Updated report object or None if not found
        """
        db_report = self.db.query(DbReport).filter(DbReport.id == report_id).first()
        if not db_report:
            return None
            
        # Update status to show we're working on it
        db_report.status = ReportStatus.GENERATING.value
        self.db.commit()
        
        if run_async:
            # Start report generation in a background thread
            threading.Thread(
                target=self._generate_report_thread,
                args=(report_id,)
            ).start()
            
            # Return the report in its current state
            return self._db_report_to_model(db_report)
        else:
            # Run synchronously
            return self._generate_report_thread(report_id)
    
    def _generate_report_thread(self, report_id: str) -> Optional[Report]:
        """
        Background thread for report generation
        
        Args:
            report_id: Report ID
            
        Returns:
            Updated report object or None if failed
        """
        try:
            # Begin by getting the report and analysis
            db_report = self.db.query(DbReport).filter(DbReport.id == report_id).first()
            if not db_report:
                logger.error(f"Report {report_id} not found in database")
                return None
            
            # Get the analysis data
            analysis_id = db_report.analysis_id
            analysis = get_analysis(self.db, analysis_id)
            if not analysis:
                error_message = f"Analysis {analysis_id} not found"
                self._update_report_status(
                    report_id, 
                    ReportStatus.FAILED, 
                    error_message=error_message
                )
                return None
            
            # Convert the analysis to the format expected by the export functions
            report_data = self._prepare_report_data(analysis, db_report.configuration)
            
            # Generate the report file
            try:
                filename = self._generate_report_file(report_id, report_data, ReportFormat(db_report.format))
                
                # Update report status
                file_size = os.path.getsize(filename)
                self._update_report_status(
                    report_id, 
                    ReportStatus.COMPLETED, 
                    file_path=str(filename),
                    file_size=file_size
                )
                
                # Return updated report
                return self.get_report(report_id)
            except Exception as e:
                logger.error(f"Error generating report file: {str(e)}", exc_info=True)
                self._update_report_status(
                    report_id, 
                    ReportStatus.FAILED, 
                    error_message=f"Error generating report file: {str(e)}"
                )
                return None
        except Exception as e:
            logger.error(f"Error in report generation thread: {str(e)}", exc_info=True)
            self._update_report_status(
                report_id, 
                ReportStatus.FAILED, 
                error_message=f"Unexpected error in report generation: {str(e)}"
            )
            return None
    
    def _update_report_status(self, 
                             report_id: str, 
                             status: ReportStatus, 
                             file_path: Optional[str] = None,
                             file_size: Optional[int] = None, 
                             error_message: Optional[str] = None) -> None:
        """
        Update the status of a report
        
        Args:
            report_id: Report ID
            status: New status
            file_path: Optional path to generated file
            file_size: Optional size of generated file
            error_message: Optional error message for failed reports
        """
        try:
            db_report = self.db.query(DbReport).filter(DbReport.id == report_id).first()
            if not db_report:
                logger.error(f"Report {report_id} not found for status update")
                return
            
            # Update status
            db_report.status = status.value
            
            # Update file info if provided
            if file_path:
                db_report.file_path = file_path
            if file_size:
                db_report.file_size = file_size
            
            # Update error info if provided
            if error_message:
                db_report.error_info = json.dumps({
                    "error_message": error_message,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Set completion timestamp if completed
            if status == ReportStatus.COMPLETED:
                db_report.completed_at = datetime.now()
            
            # Save changes
            self.db.commit()
        except Exception as e:
            logger.error(f"Error updating report status: {str(e)}", exc_info=True)
    
    def _generate_report_file(self, report_id: str, data: Dict, format: ReportFormat) -> Path:
        """
        Generate a report file in the specified format
        
        Args:
            report_id: Report ID
            data: Report data
            format: Report format
            
        Returns:
            Path to the generated file
            
        Raises:
            ValueError: If the format is unsupported
        """
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_id}_{timestamp}.{format.value}"
        output_path = self.reports_dir / filename
        
        # Generate report in requested format
        if format == ReportFormat.JSON:
            export_to_json(data, output_path)
        elif format == ReportFormat.XLSX:
            export_to_excel(data, output_path)
        elif format == ReportFormat.PDF:
            export_to_text(data, output_path.with_suffix('.txt'))
        elif format == ReportFormat.TXT:
            self._generate_txt_report(data, output_path)
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        return output_path
    
    def _generate_txt_report(self, data: Dict, output_path: Path) -> None:
        """
        Generate a text report
        
        Args:
            data: Report data
            output_path: Output file path
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("======================================\n")
            f.write("QuickTARA Security Analysis Report\n")
            f.write("======================================\n\n")
            
            # Components
            f.write("COMPONENTS\n")
            f.write("----------\n\n")
            
            for name, comp in data['components'].items():
                if not isinstance(comp, dict):
                    continue
                    
                f.write(f"Component: {name}\n")
                f.write(f"  Type: {comp.get('type', 'Unknown')}\n")
                f.write(f"  Safety Level: {comp.get('safety_level', 'Unknown')}\n")
                f.write(f"  Interfaces: {', '.join(comp.get('interfaces', []))}\n")
                f.write(f"  Access Points: {', '.join(comp.get('access_points', []))}\n")
                f.write(f"  Data Types: {', '.join(comp.get('data_types', []))}\n")
                f.write(f"  Location: {comp.get('location', 'Unknown')}\n")
                f.write(f"  Trust Zone: {comp.get('trust_zone', 'Unknown')}\n")
                f.write(f"  Connected To: {', '.join(comp.get('connected_to', []))}\n")
                
                # Threats
                if comp.get('threats'):
                    f.write("\n  Identified Threats:\n")
                    
                    for threat in comp['threats']:
                        f.write(f"  - {threat['name']}\n")
                        
                        if 'impact_scores' in threat:
                            f.write(f"    Impact Scores: {threat['impact_scores']}\n")
                        if 'risk_scores' in threat:
                            f.write(f"    Risk Scores: {threat['risk_scores']}\n")
                        if 'risk_factors' in threat:
                            risk_factors = threat['risk_factors']
                            f.write(f"    Risk Factors: {', '.join(f'{k}: {v:.2f}' for k, v in risk_factors.items())}\n")
                        
                        if 'description' in threat:
                            desc = threat['description'][:200]
                            f.write(f"    Description: {desc}...\n")
                        
                        if 'attack_chains' in threat:
                            f.write("    Attack Chains:\n")
                            for chain in threat['attack_chains']:
                                f.write(f"    * {' -> '.join(chain['chain'])}\n")
                                f.write(f"      Risk: {chain['risk_scores']}\n")
                        
                        f.write("\n")
                
                f.write("\n")
            
            # Cybersecurity Goals
            f.write("\nCYBERSECURITY GOALS\n")
            f.write("------------------\n\n")
            
            for comp_name, comp in data['components'].items():
                if isinstance(comp, dict) and 'cybersecurity_goals' in comp and comp['cybersecurity_goals']:
                    f.write(f"Component: {comp_name}\n")
                    
                    for threat_name, mappings in comp['cybersecurity_goals'].items():
                        f.write(f"  Threat: {threat_name}\n")
                        
                        if isinstance(mappings, list):
                            for mapping in mappings:
                                if isinstance(mapping, dict):
                                    f.write(f"    Goal: {mapping.get('goal', 'Unknown')} (Relevance: {mapping.get('relevance', 0)}/5)\n")
                                    f.write(f"    Description: {mapping.get('description', '')}\n")
                                    f.write("    Requirements:\n")
                                    
                                    requirements = mapping.get('requirements', [])
                                    if isinstance(requirements, list):
                                        for req in requirements[:3]:
                                            f.write(f"    - {req}\n")
                                    
                                    f.write("\n")
                        else:
                            f.write(f"    Goal: {str(mappings)}\n\n")
                    
                    f.write("\n")
            
            # Attacker Feasibility
            f.write("\nATTACKER FEASIBILITY ASSESSMENTS\n")
            f.write("-------------------------------\n\n")
            
            for comp_name, comp in data['components'].items():
                if 'feasibility_assessments' in comp and comp['feasibility_assessments']:
                    f.write(f"Component: {comp_name}\n")
                    
                    for threat_name, assessment in comp['feasibility_assessments'].items():
                        f.write(f"  Threat: {threat_name}\n")
                        f.write(f"    Feasibility Level: {assessment.get('feasibility_level', 'Medium')} ({assessment.get('overall_score', 3)}/5)\n")
                        
                        f.write("    Attack Difficulty Factors:\n")
                        f.write(f"    - Technical Capability: {assessment.get('technical_capability', 3)}/5\n")
                        f.write(f"    - Knowledge Required: {assessment.get('knowledge_required', 3)}/5\n")
                        f.write(f"    - Resources Needed: {assessment.get('resources_needed', 3)}/5\n")
                        f.write(f"    - Time Required: {assessment.get('time_required', 3)}/5\n")
                        
                        if 'profiles' in assessment:
                            profiles = assessment['profiles']
                            f.write("    Relevant Attacker Profiles:\n")
                            for profile, score in sorted(profiles.items(), key=lambda x: x[1], reverse=True)[:2]:
                                f.write(f"    - {profile}: {score}/5 relevance\n")
                        
                        if 'enabling_factors' in assessment and assessment['enabling_factors']:
                            f.write("    Enabling Factors:\n")
                            for factor in assessment['enabling_factors']:
                                f.write(f"    - {factor}\n")
                        
                        if 'mitigating_factors' in assessment and assessment['mitigating_factors']:
                            f.write("    Mitigating Factors:\n")
                            for factor in assessment['mitigating_factors']:
                                f.write(f"    - {factor}\n")
                                
                        f.write("\n")
                    
                    f.write("\n")
            
            # Risk Acceptance
            f.write("\nRISK ACCEPTANCE CRITERIA (CLAUSE 14)\n")
            f.write("----------------------------------\n\n")
            
            for comp_name, comp in data['components'].items():
                if 'risk_acceptance' in comp and comp['risk_acceptance']:
                    f.write(f"Component: {comp_name}\n")
                    
                    for threat_name, assessment in comp['risk_acceptance'].items():
                        f.write(f"  Threat: {threat_name}\n")
                        f.write(f"    Decision: {assessment.get('decision', 'Mitigate')}\n")
                        f.write(f"    Risk Severity: {assessment.get('risk_severity', 'Medium')}\n")
                        f.write(f"    Residual Risk: {assessment.get('residual_risk', 0.5):.1%}\n")
                        
                        if 'justification' in assessment and assessment['justification']:
                            f.write(f"    Justification: {assessment['justification']}\n")
                        
                        if 'conditions' in assessment and assessment['conditions']:
                            f.write("    Conditions:\n")
                            for condition in assessment['conditions'][:3]:
                                f.write(f"    - {condition}\n")
                        
                        if 'approvers' in assessment and assessment['approvers']:
                            f.write("    Required Approvals:\n")
                            for approver in assessment['approvers']:
                                f.write(f"    - {approver}\n")
                        
                        if 'criteria' in assessment and 'reassessment_period' in assessment['criteria']:
                            period = assessment['criteria']['reassessment_period']
                            f.write(f"    Reassessment Period: {period} months\n")
                        
                        f.write("\n")
                    
                    f.write("\n")
            
            # Risk Treatment Reviews
            has_reviews = any('reviewer' in comp.get('risk_acceptance', {}).get(threat_name, {}) 
                             for comp in data['components'].values() 
                             for threat_name in comp.get('risk_acceptance', {}))
            
            if has_reviews:
                f.write("\nRISK TREATMENT REVIEWS\n")
                f.write("---------------------\n\n")
                
                for comp_name, comp in data['components'].items():
                    if 'risk_acceptance' in comp:
                        has_comp_reviews = any('reviewer' in assessment for assessment in comp['risk_acceptance'].values())
                        if has_comp_reviews:
                            f.write(f"Component: {comp_name}\n")
                            
                            for threat_name, assessment in comp['risk_acceptance'].items():
                                if 'reviewer' in assessment:
                                    f.write(f"  Threat: {threat_name}\n")
                                    
                                    final_decision = assessment.get('decision', 'Mitigate')
                                    original_decision = assessment.get('original_decision', final_decision)
                                    
                                    f.write(f"    Review Status: Reviewed\n")
                                    f.write(f"    Final Decision: {final_decision}\n")
                                    
                                    if original_decision != final_decision:
                                        f.write(f"    Original Decision: {original_decision}\n")
                                    
                                    f.write(f"    Reviewer: {assessment.get('reviewer', '')}\n")
                                    f.write(f"    Review Date: {assessment.get('review_date', '')}\n")
                                    
                                    f.write(f"    Justification: {assessment.get('justification', '')}\n")
                                    
                                    if 'additional_notes' in assessment and assessment['additional_notes']:
                                        f.write(f"    Additional Notes: {assessment['additional_notes']}\n")
                                    
                                    if 'evidence_references' in assessment and assessment['evidence_references']:
                                        f.write("    Evidence References:\n")
                                        for evidence in assessment['evidence_references']:
                                            f.write(f"    - {evidence}\n")
                                    
                                    f.write("\n")
                            
                            f.write("\n")
    
    def _prepare_report_data(self, analysis: Analysis, config: Dict) -> Dict:
        """
        Prepare analysis data for report generation
        
        Args:
            analysis: Analysis object
            config: Report configuration
            
        Returns:
            Dictionary with report data
        """
        # Start with basic analysis info
        report_data = {
            "id": analysis.id,
            "name": analysis.name,
            "description": analysis.description,
            "created_at": analysis.created_at.isoformat(),
            "components": {},
            "summary": {
                "total_components": analysis.summary.total_components,
                "total_threats": analysis.summary.total_threats,
                "critical_components": analysis.summary.critical_components,
                "high_risk_threats": analysis.summary.high_risk_threats
            }
        }
        
        # Process components based on configuration
        include_components = config.get('include_components', True)
        include_threats = config.get('include_threats', True)
        include_stride = config.get('include_stride', True)
        include_compliance = config.get('include_compliance', True)
        include_attacker_feasibility = config.get('include_attacker_feasibility', True)
        include_risk_acceptance = config.get('include_risk_acceptance', True)
        include_attack_paths = config.get('include_attack_paths', True)
        include_review_decisions = config.get('include_review_decisions', True)
        
        # Max threats per component (0 = all)
        max_threats = config.get('max_threats_per_component', 0)
        
        # Process each component
        for comp_id, comp_analysis in analysis.components.items():
            # Create component data
            component_data = {
                "name": comp_analysis.name,
                "type": comp_analysis.type,
                "safety_level": comp_analysis.safety_level,
                "interfaces": [],
                "access_points": [],
                "data_types": [],
                "location": "Unknown",
                "trust_zone": "Unknown",
                "connected_to": []
            }
            
            # Add threats if included
            if include_threats:
                threats = comp_analysis.threats
                if max_threats > 0:
                    threats = threats[:max_threats]
                
                component_data["threats"] = [
                    {
                        "name": threat.name,
                        "description": threat.description,
                        "likelihood": threat.likelihood,
                        "impact_scores": {
                            "financial": threat.impact.financial,
                            "safety": threat.impact.safety,
                            "privacy": threat.impact.privacy
                        },
                        "risk_scores": {
                            "financial": threat.likelihood * threat.impact.financial,
                            "safety": threat.likelihood * threat.impact.safety,
                            "privacy": threat.likelihood * threat.impact.privacy
                        },
                        "risk_factors": {
                            "exposure": threat.risk_factors.exposure,
                            "complexity": threat.risk_factors.complexity,
                            "attack_surface": threat.risk_factors.attack_surface
                        }
                    }
                    for threat in threats
                ]
            
            # Add STRIDE analysis if included
            if include_stride:
                component_data["stride_analysis"] = {
                    category: {
                        "risk_level": recommendation.risk_level,
                        "recommendations": recommendation.recommendations
                    }
                    for category, recommendation in comp_analysis.stride_analysis.items()
                }
            
            # Add compliance requirements if included
            if include_compliance:
                component_data["compliance"] = [
                    {
                        "standard": req.standard,
                        "requirement": req.requirement,
                        "description": req.description
                    }
                    for req in comp_analysis.compliance
                ]
            
            # Add attacker feasibility assessments if included
            if include_attacker_feasibility:
                component_data["feasibility_assessments"] = {
                    threat_name: {
                        "feasibility_level": assessment.feasibility_level,
                        "technical_capability": assessment.technical_capability,
                        "knowledge_required": assessment.knowledge_required,
                        "resources_needed": assessment.resources_needed,
                        "time_required": assessment.time_required,
                        "overall_score": assessment.overall_score,
                        "enabling_factors": assessment.enabling_factors,
                        "mitigating_factors": assessment.mitigating_factors,
                        "profiles": {
                            profile.profile_type: profile.relevance
                            for profile in assessment.attacker_profiles
                        }
                    }
                    for threat_name, assessment in comp_analysis.feasibility_assessments.items()
                }
            
            # Add risk acceptance decisions if included
            if include_risk_acceptance:
                component_data["risk_acceptance"] = {
                    threat_name: {
                        "decision": acceptance.decision,
                        "risk_severity": acceptance.risk_severity,
                        "residual_risk": acceptance.residual_risk,
                        "justification": acceptance.justification,
                        "conditions": acceptance.conditions,
                        "approvers": acceptance.approvers,
                        "criteria": {
                            "reassessment_period": acceptance.reassessment_period
                        }
                    }
                    for threat_name, acceptance in comp_analysis.risk_acceptance.items()
                }
            
            # Add attack paths if included
            if include_attack_paths:
                component_data["attack_paths"] = [
                    {
                        "chain": path.path,
                        "risk_scores": path.risk
                    }
                    for path in comp_analysis.attack_paths
                ]
            
            # Add to components
            report_data["components"][comp_id] = component_data
        
        return report_data
    
    def _db_report_to_model(self, db_report: DbReport) -> Report:
        """Convert database report to Pydantic model"""
        config = db_report.configuration if db_report.configuration else {}
        
        # Parse error info if exists
        error_info = None
        if db_report.error_info:
            try:
                error_data = json.loads(db_report.error_info)
                error_info = ReportError(
                    report_id=db_report.id,
                    error_message=error_data.get('error_message', 'Unknown error'),
                    error_details=error_data.get('error_details'),
                    timestamp=datetime.fromisoformat(error_data.get('timestamp', datetime.now().isoformat()))
                )
            except Exception as e:
                logger.warning(f"Error parsing error info: {str(e)}")
                error_info = ReportError(
                    report_id=db_report.id,
                    error_message=str(db_report.error_info),
                    timestamp=datetime.now()
                )
        
        return Report(
            id=db_report.id,
            analysis_id=db_report.analysis_id,
            name=db_report.name,
            description=db_report.description,
            format=ReportFormat(db_report.format),
            report_type=ReportType(db_report.report_type),
            status=ReportStatus(db_report.status),
            file_path=db_report.file_path,
            file_size=db_report.file_size,
            created_at=db_report.created_at,
            completed_at=db_report.completed_at,
            configuration=ReportConfiguration(**(config or {})),
            error=error_info
        )
    
    def _db_report_to_summary(self, db_report: DbReport) -> ReportSummary:
        """Convert database report to summary model"""
        return ReportSummary(
            id=db_report.id,
            analysis_id=db_report.analysis_id,
            name=db_report.name,
            format=ReportFormat(db_report.format),
            report_type=ReportType(db_report.report_type),
            status=ReportStatus(db_report.status),
            created_at=db_report.created_at
        )
