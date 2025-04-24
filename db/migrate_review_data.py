#!/usr/bin/env python3
"""
Script to migrate review decisions from JSON files to the database

This script reads existing review decision files and migrates them to the new
database table structure.
"""
import os
import sys
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

# Add the project root to sys.path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.session import get_engine
from db.base import Base, ReviewDecision

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("migrate_review_data")


def load_review_decisions_from_file(file_path):
    """
    Load review decisions from a JSON file
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary of review decisions
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading review decisions from {file_path}: {e}")
        return {}


def find_review_files(uploads_dir=None):
    """
    Find all review decision files
    
    Args:
        uploads_dir: Directory containing review files
        
    Returns:
        List of file paths
    """
    if uploads_dir is None:
        uploads_dir = Path("uploads/reviews")
    
    if not uploads_dir.exists():
        logger.warning(f"Uploads directory {uploads_dir} does not exist")
        return []
    
    review_files = []
    for file_path in uploads_dir.glob("*_reviews.json"):
        if file_path.is_file():
            review_files.append(file_path)
    
    logger.info(f"Found {len(review_files)} review files")
    return review_files


def migrate_reviews(db_session):
    """
    Migrate review decisions from files to database
    
    Args:
        db_session: Database session
        
    Returns:
        Number of migrated review decisions
    """
    # Find review files
    review_files = find_review_files()
    
    total_migrated = 0
    
    for file_path in review_files:
        try:
            # Extract analysis_id from filename
            filename = file_path.name
            analysis_id = filename.split('_reviews.json')[0]
            
            logger.info(f"Processing reviews for analysis {analysis_id}")
            
            # Load review decisions from file
            review_data = load_review_decisions_from_file(file_path)
            
            # Process each component and threat
            for component_id, threats in review_data.items():
                for threat_id, decision_data in threats.items():
                    # Check if review decision already exists
                    existing = db_session.query(ReviewDecision).filter_by(
                        analysis_id=analysis_id,
                        component_id=component_id,
                        threat_id=threat_id
                    ).first()
                    
                    if existing:
                        logger.info(f"Review decision for analysis {analysis_id}, component {component_id}, threat {threat_id} already exists")
                        continue
                    
                    # Create review decision object
                    review_decision = ReviewDecision(
                        id=str(uuid.uuid4()),
                        analysis_id=analysis_id,
                        component_id=component_id,
                        threat_id=threat_id,
                        original_decision=decision_data.get('original_decision', 'Mitigate'),
                        final_decision=decision_data.get('final_decision', 'Mitigate'),
                        reviewer=decision_data.get('reviewer', ''),
                        justification=decision_data.get('justification', ''),
                        additional_notes=decision_data.get('additional_notes', ''),
                        review_date=decision_data.get('review_date', datetime.now().strftime('%Y-%m-%d')),
                        evidence_references=decision_data.get('evidence_references', []),
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        status='completed'  # Assume all migrated reviews are completed
                    )
                    
                    # Add to database
                    db_session.add(review_decision)
                    total_migrated += 1
            
            # Commit changes for this file
            db_session.commit()
            logger.info(f"Migrated reviews for analysis {analysis_id}")
            
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error migrating reviews from {file_path}: {e}")
    
    return total_migrated


def main():
    """Main function"""
    # Create database engine and session
    engine = get_engine()
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    # Create database session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Migrate review decisions
        migrated_count = migrate_reviews(session)
        logger.info(f"Successfully migrated {migrated_count} review decisions")
    finally:
        session.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
