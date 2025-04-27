"""
Script to directly set up Attack Path Analysis tables and populate them with sample data.
This is an alternative to using Alembic migrations when there are issues with the migration system.
"""
import os
import sys
import logging
from datetime import datetime
import uuid
import json

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project's database modules
from db.session import SessionLocal, engine
from db.base import Base
from db.attack_path import AttackStep, AttackPath, AttackChain, chain_paths
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_tables():
    """Create the attack path analysis tables if they don't exist"""
    try:
        # Create tables for attack path analysis
        # We're using the existing Base class that the models are already attached to
        Base.metadata.create_all(bind=engine, tables=[
            AttackStep.__table__,
            AttackPath.__table__,
            AttackChain.__table__,
            chain_paths
        ])
        logger.info("Attack path analysis tables created successfully.")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error creating tables: {str(e)}")
        return False


def create_sample_data():
    """Create sample data for testing the Attack Path Analysis functionality"""
    try:
        db = SessionLocal()
        
        # Check if we already have sample data
        existing_paths = db.query(AttackPath).count()
        if existing_paths > 0:
            logger.info("Sample data already exists, skipping creation.")
            db.close()
            return True
            
        # Create a sample analysis if needed
        from sqlalchemy import text
        result = db.execute(text("SELECT id FROM analyses LIMIT 1")).fetchone()
        if result:
            analysis_id = result[0]
        else:
            # Create a new analysis record
            analysis_id = f"analysis_{uuid.uuid4().hex}"
            db.execute(
                text("INSERT INTO analyses (id, name, description, created_at) VALUES (:id, :name, :desc, :created)"),
                {"id": analysis_id, "name": "Sample Attack Path Analysis", "desc": "Test analysis for attack paths", "created": datetime.now()}
            )
        
        # Get sample components
        components = db.execute(text("SELECT component_id, name, type FROM components LIMIT 10")).fetchall()
        
        if not components or len(components) < 5:
            # Create sample components if not enough exist
            sample_components = [
                ("comp_ecm", "Engine Control Module", "ECU"),
                ("comp_tcm", "Transmission Control Module", "ECU"),
                ("comp_bcm", "Body Control Module", "ECU"),
                ("comp_telematics", "Telematics Unit", "Connectivity"),
                ("comp_gateway", "Central Gateway", "Gateway"),
                ("comp_infotainment", "Infotainment System", "HMI"),
                ("comp_obd", "OBD-II Port", "Interface"),
                ("comp_can_bus", "CAN Bus Network", "Network"),
                ("comp_bluetooth", "Bluetooth Module", "Connectivity"),
                ("comp_usb", "USB Port", "Interface")
            ]
            
            for comp_id, name, comp_type in sample_components:
                db.execute(
                    text("INSERT INTO components (component_id, name, type, trust_zone, safety_level) "
                         "VALUES (:id, :name, :type, :trust, :safety) "
                         "ON CONFLICT (component_id) DO NOTHING"),
                    {
                        "id": comp_id,
                        "name": name,
                        "type": comp_type,
                        "trust": "Standard" if "ECU" in comp_type else "Boundary",
                        "safety": "ASIL B" if "ECU" in comp_type else "QM"
                    }
                )
            
            # Update components list with our new components
            components = db.execute(text("SELECT component_id, name, type FROM components LIMIT 10")).fetchall()
        
        # Create sample attack paths
        paths = []
        for i in range(3):
            # Use different components for entry and target
            entry_index = i % len(components)
            target_index = (i + 3) % len(components)
            
            entry_point = components[entry_index]
            target = components[target_index]
            
            path_id = f"path_{uuid.uuid4().hex}"
            path_type = ["Direct", "Multi-Step", "Lateral", "Privilege Escalation"][i % 4]
            complexity = ["Low", "Medium", "High"][i % 3]
            
            # Create impact data
            impact = {
                "confidentiality": 5 + (i % 6),
                "integrity": 6 + (i % 5),
                "availability": 7 + (i % 4)
            }
            
            # Calculate likelihood and risk score
            likelihood = 0.8 - (i * 0.2)
            risk_score = likelihood * max(impact.values())
            
            # Create a new path
            path = AttackPath(
                path_id=path_id,
                analysis_id=analysis_id,
                name=f"Attack Path {entry_point[1]} → {target[1]}",
                description=f"Sample attack path from {entry_point[1]} to {target[1]}",
                path_type=path_type,
                complexity=complexity,
                entry_point_id=entry_point[0],
                target_id=target[0],
                success_likelihood=likelihood,
                impact=impact,
                risk_score=risk_score
            )
            db.add(path)
            paths.append(path)
            
            # Create steps for this path
            num_steps = 2 + i  # Between 2 and 4 steps
            for j in range(num_steps):
                # Determine the component for this step
                if j == 0:
                    component_id = entry_point[0]  # First step is the entry point
                elif j == num_steps - 1:
                    component_id = target[0]  # Last step is the target
                else:
                    # Intermediate step
                    intermediate_index = (entry_index + j) % len(components)
                    component_id = components[intermediate_index][0]
                
                # Determine step type
                if j == 0:
                    step_type = "Initial Access"
                elif j == num_steps - 1:
                    step_type = "Impact"
                else:
                    step_type = ["Execution", "Persistence", "Privilege Escalation", "Lateral Movement"][j % 4]
                
                # Create step description
                if j == 0:
                    description = f"Initial access via {components[entry_index][1]}"
                elif j == num_steps - 1:
                    description = f"Compromise {components[target_index][1]} to achieve attack objective"
                else:
                    prev_comp = components[(entry_index + j - 1) % len(components)][1]
                    curr_comp = components[(entry_index + j) % len(components)][1]
                    description = f"Move from {prev_comp} to {curr_comp}"
                
                # Create step
                step = AttackStep(
                    step_id=f"step_{uuid.uuid4().hex}",
                    path_id=path_id,
                    component_id=component_id,
                    step_type=step_type,
                    description=description,
                    prerequisites=[],
                    vulnerability_ids=[],
                    threat_ids=[],
                    order=j
                )
                db.add(step)
        
        # Create a sample attack chain linking the paths
        if paths:
            chain_id = f"chain_{uuid.uuid4().hex}"
            entry_points = [path.entry_point_id for path in paths]
            targets = [path.target_id for path in paths]
            
            # Average likelihood and max impact
            avg_likelihood = sum(path.success_likelihood for path in paths) / len(paths)
            max_confidentiality = max(path.impact["confidentiality"] for path in paths)
            max_integrity = max(path.impact["integrity"] for path in paths)
            max_availability = max(path.impact["availability"] for path in paths)
            
            impact = {
                "confidentiality": max_confidentiality,
                "integrity": max_integrity,
                "availability": max_availability
            }
            
            risk_score = avg_likelihood * max(impact.values())
            
            # Create chain
            chain = AttackChain(
                chain_id=chain_id,
                analysis_id=analysis_id,
                name=f"Attack Chain {len(paths)} Paths",
                description="Sample attack chain combining multiple paths",
                entry_points=entry_points,
                targets=targets,
                attack_goal="Vehicle Control System Compromise",
                complexity="Medium",
                success_likelihood=avg_likelihood,
                impact=impact,
                risk_score=risk_score
            )
            db.add(chain)
            
            # Link paths to chain
            for path in paths:
                db.execute(
                    text("INSERT INTO attack_chain_paths (chain_id, path_id) VALUES (:chain_id, :path_id)"),
                    {"chain_id": chain_id, "path_id": path.path_id}
                )
        
        db.commit()
        logger.info("Sample data created successfully.")
        db.close()
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Error creating sample data: {str(e)}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False


if __name__ == "__main__":
    # Set up the tables
    if setup_tables():
        # Create sample data
        create_sample_data()
    else:
        logger.error("Failed to set up attack path analysis tables.")
        sys.exit(1)
