"""
Component service layer
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import csv
from io import StringIO
import json

from db.base import Component as DBComponent
from api.models.component import Component, ComponentCreate, ComponentUpdate


def create_component(db: Session, component: ComponentCreate) -> Component:
    """
    Create a new component in the database
    """
    # Check if component with same ID already exists
    existing = db.query(DBComponent).filter(DBComponent.component_id == component.component_id).first()
    if existing:
        raise ValueError(f"Component with ID {component.component_id} already exists")
    
    # Convert list fields to JSON
    db_component = DBComponent(
        component_id=component.component_id,
        name=component.name,
        type=component.type,
        safety_level=component.safety_level,
        interfaces=json.dumps(component.interfaces),
        access_points=json.dumps(component.access_points),
        data_types=json.dumps(component.data_types),
        location=component.location,
        trust_zone=component.trust_zone,
        scope_id=component.scope_id,
        # Add security properties (C-I-A)
        confidentiality=component.confidentiality,
        integrity=component.integrity, 
        availability=component.availability,
        authenticity_required=component.authenticity_required,
        authorization_required=component.authorization_required
    )
    
    # Add to database
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    
    # Handle connections separately (many-to-many relationship)
    connected_components = []
    for connected_id in component.connected_to:
        connected = db.query(DBComponent).filter(DBComponent.component_id == connected_id).first()
        if connected:
            connected_components.append(connected)
    
    if connected_components:
        db_component.connected_to = connected_components
        db.commit()
        db.refresh(db_component)
    
    return _db_component_to_schema(db_component)


def get_component(db: Session, component_id: str) -> Optional[Component]:
    """
    Get a component by ID
    """
    db_component = db.query(DBComponent).filter(DBComponent.component_id == component_id).first()
    if not db_component:
        return None
    
    return _db_component_to_schema(db_component)


def get_components(db: Session, skip: int = 0, limit: int = 100) -> List[Component]:
    """
    Get all components with pagination
    """
    try:
        # Use a try-except block to handle potential database issues with schema
        db_components = db.query(DBComponent).offset(skip).limit(limit).all()
        return [_db_component_to_schema(c) for c in db_components]
    except Exception as e:
        # Handle the case where schema might be outdated
        try:
            # Try a more complete SQL query that includes all fields
            from sqlalchemy import text
            result = db.execute(text(
                "SELECT c.component_id, c.name, c.type, c.safety_level, c.interfaces, "
                "c.access_points, c.data_types, c.location, c.trust_zone, "
                "c.scope_id, c.confidentiality, c.integrity, c.availability, "
                "c.authenticity_required, c.authorization_required "
                "FROM components c LIMIT :limit OFFSET :skip"
            ), {"skip": skip, "limit": limit})
            
            # Get connected components with a separate query for each component
            components = []
            for row in result:
                # Get connected components for this component
                connected_to = []
                try:
                    connections = db.execute(text(
                        "SELECT connected_to_id FROM component_connections "
                        "WHERE component_id = :component_id"
                    ), {"component_id": row[0]})
                    connected_to = [conn[0] for conn in connections]
                except Exception:
                    # If connections query fails, leave as empty list
                    pass
                
                # Normalize security properties to title case (High, Medium, Low, N/A)
                def normalize_security_level(value):
                    if not value:
                        return "Medium"  # Default
                    # Convert to title case (first letter uppercase, rest lowercase)
                    if value.upper() == "N/A":
                        return "N/A"
                    return value.title()
                
                # Create a complete component from the raw SQL result
                component = Component(
                    component_id=row[0],
                    name=row[1],
                    type=row[2],
                    safety_level=row[3],
                    interfaces=_parse_json_list(row[4]),
                    access_points=_parse_json_list(row[5]),
                    data_types=_parse_json_list(row[6]),
                    location=row[7] or "",
                    trust_zone=row[8] or "",
                    scope_id=row[9],  # Include scope_id
                    confidentiality=normalize_security_level(row[10]),  # Normalize CIA properties
                    integrity=normalize_security_level(row[11]),
                    availability=normalize_security_level(row[12]),
                    authenticity_required=bool(row[13]) if row[13] is not None else False,
                    authorization_required=bool(row[14]) if row[14] is not None else False,
                    connected_to=connected_to  # Include connected components
                )
                components.append(component)
            return components
        except Exception as inner_e:
            # If both methods fail, log the error and re-raise
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in get_components: {str(e)} | Fallback error: {str(inner_e)}")
            raise


def count_components(db: Session) -> int:
    """
    Count total number of components
    """
    try:
        return db.query(DBComponent).count()
    except Exception:
        # Fallback to direct SQL if ORM query fails
        try:
            from sqlalchemy import text
            result = db.execute(text("SELECT COUNT(*) FROM components"))
            return result.scalar() or 0
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in count_components: {str(e)}")
            return 0  # Safe fallback


def get_components_by_scope(db: Session, scope_id: str, skip: int = 0, limit: int = 100) -> List[Component]:
    """
    Get components filtered by scope ID
    """
    db_components = db.query(DBComponent).filter(DBComponent.scope_id == scope_id).offset(skip).limit(limit).all()
    return [_db_component_to_schema(c) for c in db_components]


def count_components_by_scope(db: Session, scope_id: str) -> int:
    """
    Count total number of components for a specific scope
    """
    return db.query(DBComponent).filter(DBComponent.scope_id == scope_id).count()


def update_component(db: Session, component_id: str, component: ComponentUpdate) -> Optional[Component]:
    """
    Update an existing component
    """
    db_component = db.query(DBComponent).filter(DBComponent.component_id == component_id).first()
    if not db_component:
        return None
    
    # Update fields if provided
    update_data = component.dict(exclude_unset=True)
    
    # Handle list fields - convert to JSON if present
    if "interfaces" in update_data:
        update_data["interfaces"] = json.dumps(update_data["interfaces"])
    if "access_points" in update_data:
        update_data["access_points"] = json.dumps(update_data["access_points"])
    if "data_types" in update_data:
        update_data["data_types"] = json.dumps(update_data["data_types"])
    
    # Handle connected_to separately (many-to-many)
    if "connected_to" in update_data:
        connected_ids = update_data.pop("connected_to")
        connected_components = []
        for connected_id in connected_ids:
            connected = db.query(DBComponent).filter(DBComponent.component_id == connected_id).first()
            if connected:
                connected_components.append(connected)
        db_component.connected_to = connected_components
    
    # Relationship and simple attribute updates
    if "scope_id" in update_data:
        db_component.scope_id = update_data.pop("scope_id")
    
    # Update other attributes
    for key, value in update_data.items():
        setattr(db_component, key, value)
    
    db.commit()
    db.refresh(db_component)
    # Refresh again to get connections and scope relationship updates
    db.refresh(db_component)
    
    return _db_component_to_schema(db_component)


def delete_component(db: Session, component_id: str) -> bool:
    """
    Delete a component by ID
    """
    db_component = db.query(DBComponent).filter(DBComponent.component_id == component_id).first()
    if not db_component:
        return False
    
    db.delete(db_component)
    db.commit()
    return True


def import_components_from_csv(db: Session, csv_content: str) -> Dict[str, Any]:
    """
    Import components from CSV content
    """
    csv_reader = csv.DictReader(StringIO(csv_content))
    
    imported = 0
    skipped = 0
    errors = []
    
    for row in csv_reader:
        try:
            # Parse row into ComponentCreate model
            component_data = {
                "component_id": row["component_id"].strip(),
                "name": row["name"].strip(),
                "type": row["type"].strip(),
                "safety_level": row["safety_level"].strip(),
                "interfaces": [i.strip() for i in row["interfaces"].split("|") if i.strip()],
                "access_points": [a.strip() for a in row["access_points"].split("|") if a.strip()],
                "data_types": [d.strip() for d in row["data_types"].split("|") if d.strip()],
                "location": row["location"].strip(),
                "trust_zone": row["trust_zone"].strip(),
                "connected_to": [c.strip() for c in row["connected_to"].split("|") if c.strip()],
            }
            
            # Parse security properties if present in CSV
            if "confidentiality" in row:
                component_data["confidentiality"] = row["confidentiality"].strip()
            if "integrity" in row:
                component_data["integrity"] = row["integrity"].strip()
            if "availability" in row:
                component_data["availability"] = row["availability"].strip()
            if "authenticity_required" in row:
                component_data["authenticity_required"] = row["authenticity_required"].lower() == "true"
            if "authorization_required" in row:
                component_data["authorization_required"] = row["authorization_required"].lower() == "true"
            
            component = ComponentCreate(**component_data)
            
            # Check if component already exists
            existing = db.query(DBComponent).filter(DBComponent.component_id == component.component_id).first()
            if existing:
                skipped += 1
                continue
            
            # Create component
            create_component(db, component)
            imported += 1
            
        except Exception as e:
            errors.append({
                "row": dict(row),
                "error": str(e)
            })
    
    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors
    }


def export_components_to_csv(db: Session) -> str:
    """
    Export all components to CSV format
    """
    components = get_components(db, skip=0, limit=1000)  # Limit for safety
    
    output = StringIO()
    fieldnames = [
        "component_id", "name", "type", "safety_level", "interfaces",
        "access_points", "data_types", "location", "trust_zone", "connected_to",
        # Add security properties
        "confidentiality", "integrity", "availability",
        "authenticity_required", "authorization_required"
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for component in components:
        writer.writerow({
            "component_id": component.component_id,
            "name": component.name,
            "type": component.type,
            "safety_level": component.safety_level,
            "interfaces": "|".join(component.interfaces),
            "access_points": "|".join(component.access_points),
            "data_types": "|".join(component.data_types),
            "location": component.location,
            "trust_zone": component.trust_zone,
            "connected_to": "|".join(component.connected_to),
            # Add security properties
            "confidentiality": component.confidentiality,
            "integrity": component.integrity,
            "availability": component.availability,
            "authenticity_required": str(component.authenticity_required).lower(),
            "authorization_required": str(component.authorization_required).lower(),
        })
    
    return output.getvalue()


def _parse_json_list(val: str):
    """Return a Python list from a column that may contain JSON or double-encoded JSON."""
    if not val:
        return []
    try:
        parsed = json.loads(val)
        # If the first load still returns a string (double-encoded), try again
        if isinstance(parsed, str):
            try:
                parsed = json.loads(parsed)
            except Exception:
                pass
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    # Fall back to treating comma-separated string as list
    if isinstance(val, str):
        return [v.strip() for v in val.split(',') if v.strip()]
    return []


def _db_component_to_schema(db_component: DBComponent) -> Component:
    """
    Convert DB component to Pydantic schema
    """
    # Parse JSON fields
    interfaces = _parse_json_list(db_component.interfaces)
    access_points = _parse_json_list(db_component.access_points)
    data_types = _parse_json_list(db_component.data_types)
    
    # Get connected component IDs
    connected_to = [c.component_id for c in db_component.connected_to]
    
    # Handle scope_id (may not exist in database yet)
    scope_id = getattr(db_component, 'scope_id', None)
    
    # Get CIA security properties, with fallbacks for older database records
    confidentiality = getattr(db_component, 'confidentiality', "Medium")
    integrity = getattr(db_component, 'integrity', "Medium")
    availability = getattr(db_component, 'availability', "Medium")
    authenticity_required = getattr(db_component, 'authenticity_required', False)
    authorization_required = getattr(db_component, 'authorization_required', False)
    
    return Component(
        component_id=db_component.component_id,
        name=db_component.name,
        type=db_component.type,
        safety_level=db_component.safety_level,
        interfaces=interfaces,
        access_points=access_points,
        data_types=data_types,
        location=db_component.location,
        trust_zone=db_component.trust_zone,
        connected_to=connected_to,
        scope_id=scope_id,
        # Include CIA security properties
        confidentiality=confidentiality,
        integrity=integrity,
        availability=availability,
        authenticity_required=authenticity_required,
        authorization_required=authorization_required
    )
