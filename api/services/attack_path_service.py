"""
Service for Attack Path Analysis
"""
import uuid
import logging
import networkx as nx
from typing import List, Dict, Optional, Any, Tuple, Set, Union
from datetime import datetime
from sqlalchemy.orm import Session

from db.attack_path import AttackPath, AttackStep, AttackChain, chain_paths
from db.base import Component
from api.models.attack_path import (
    AttackPathType, AttackStepType, AttackComplexity,
    PathCreate, StepCreate, ChainCreate, 
    AttackPathRequest, AttackPathAnalysisResult
)

logger = logging.getLogger(__name__)


class AttackPathService:
    """Service for Attack Path Analysis"""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def generate_attack_paths(self, request: AttackPathRequest) -> AttackPathAnalysisResult:
        """
        Generate attack paths for the given components.
        
        This is the main entry point for attack path analysis.
        """
        logger.info(f"Generating attack paths for {len(request.component_ids)} components")
        
        # Get analysis ID or generate a new one
        analysis_id = request.analysis_id or f"attack_analysis_{uuid.uuid4().hex}"
        
        # Get components from database
        components = self._get_components(request.component_ids)
        if not components:
            raise ValueError("No valid components found for analysis")
            
        # Identify entry points and targets
        entry_points = self._identify_entry_points(components, request.entry_point_ids)
        targets = self._identify_targets(components, request.target_ids)
        
        if not entry_points:
            raise ValueError("No valid entry points identified")
        if not targets:
            raise ValueError("No valid targets identified")
            
        # Build component graph
        component_graph = self._build_component_graph(components)
        
        # Generate attack paths
        paths = self._generate_paths(
            component_graph, 
            entry_points, 
            targets, 
            analysis_id, 
            request.scope_id,
            request.max_depth
        )
        
        # If requested, generate attack chains
        chains = []
        if request.include_chains and paths:
            chains = self._generate_chains(paths, analysis_id, request.scope_id)
            
        # Create and save result
        result = self._create_analysis_result(
            analysis_id=analysis_id,
            components=components,
            entry_points=entry_points,
            targets=targets,
            paths=paths,
            chains=chains,
            scope_id=request.scope_id
        )
        
        return result
        
    def _get_components(self, component_ids: List[str]) -> List[Component]:
        """Get components from database by their IDs"""
        return self.db.query(Component).filter(Component.component_id.in_(component_ids)).all()
        
    def _identify_entry_points(
        self, 
        components: List[Component], 
        entry_point_ids: Optional[List[str]] = None
    ) -> List[Component]:
        """
        Identify entry points from components.
        
        Entry points are components that:
        1. Are explicitly specified as entry points, if provided
        2. Have external location
        3. Have public access points
        4. Are in untrusted or boundary trust zones
        """
        if entry_point_ids:
            # Use explicitly specified entry points
            return [c for c in components if c.component_id in entry_point_ids]
            
        # Identify entry points based on component properties
        entry_points = []
        for component in components:
            # Check if component has external location
            if component.location.lower() == "external":
                entry_points.append(component)
                continue
                
            # Check if component has public access points
            access_points = component.access_points or []
            if isinstance(access_points, str):
                access_points = access_points.split("|")
                
            public_access_points = ["internet", "public", "wireless", "ota", "usb", "bluetooth"]
            for ap in access_points:
                if any(p in ap.lower() for p in public_access_points):
                    entry_points.append(component)
                    break
                    
            # Check if component is in untrusted or boundary zone
            if not entry_points and component.trust_zone.lower() in ["untrusted", "boundary"]:
                entry_points.append(component)
                
        return entry_points
        
    def _identify_targets(
        self, 
        components: List[Component], 
        target_ids: Optional[List[str]] = None
    ) -> List[Component]:
        """
        Identify targets from components.
        
        Targets are components that:
        1. Are explicitly specified as targets, if provided
        2. Have high safety level (ASIL C or D)
        3. Are in critical trust zones
        4. Have sensitive data types
        """
        if target_ids:
            # Use explicitly specified targets
            return [c for c in components if c.component_id in target_ids]
            
        # Identify targets based on component properties
        targets = []
        for component in components:
            # Check if component has high safety level
            if component.safety_level.upper() in ["ASIL C", "ASIL D"]:
                targets.append(component)
                continue
                
            # Check if component is in critical zone
            if component.trust_zone.lower() == "critical":
                targets.append(component)
                continue
                
            # Check if component has sensitive data types
            data_types = component.data_types or []
            if isinstance(data_types, str):
                data_types = data_types.split("|")
                
            sensitive_data_types = ["key", "credential", "personal", "safety", "control"]
            for dt in data_types:
                if any(s in dt.lower() for s in sensitive_data_types):
                    targets.append(component)
                    break
                    
        return targets
        
    def _build_component_graph(self, components: List[Component]) -> nx.DiGraph:
        """
        Build a directed graph representing component connections.
        
        This graph will be used for path finding. Each edge has attributes:
        - trust_boundary: Whether this connection crosses trust boundaries
        - complexity: Complexity of exploiting this connection
        """
        G = nx.DiGraph()
        
        # Add nodes (components)
        for component in components:
            G.add_node(
                component.component_id,
                name=component.name,
                type=component.type,
                trust_zone=component.trust_zone,
                interfaces=component.interfaces,
                safety_level=component.safety_level
            )
            
        # Add edges (connections)
        for component in components:
            connected_to = []
            
            # Get connections from ORM relationship - this is how the project handles connections
            if hasattr(component, 'connected_to') and component.connected_to:
                # The project uses a many-to-many relationship with the component_connections table
                connected_to = [c.component_id for c in component.connected_to]
            
            # Query the component_connections table directly as fallback
            if not connected_to:
                # Execute a direct query to get connections using SQLAlchemy's text() function
                from sqlalchemy import text
                result = self.db.execute(
                    text("SELECT connected_to_id FROM component_connections WHERE component_id = :comp_id"),
                    {"comp_id": component.component_id}
                ).fetchall()
                connected_to = [row[0] for row in result]
            
            for target_id in connected_to:
                # Find target component
                target = next((c for c in components if c.component_id == target_id), None)
                if not target:
                    continue
                    
                # Check if connection crosses trust boundaries
                trust_boundary = component.trust_zone != target.trust_zone
                
                # Determine complexity based on properties
                complexity = self._calculate_connection_complexity(component, target, trust_boundary)
                
                # Add edge with attributes
                G.add_edge(
                    component.component_id,
                    target_id,
                    trust_boundary=trust_boundary,
                    complexity=complexity
                )
                
        return G
        
    def _calculate_connection_complexity(
        self, 
        source: Component, 
        target: Component, 
        trust_boundary: bool
    ) -> str:
        """Calculate the complexity of exploiting a connection between components"""
        # Base complexity
        if trust_boundary:
            complexity = "HIGH"
        else:
            complexity = "MEDIUM"
            
        # Adjust based on safety level
        source_safety = source.safety_level.upper() if source.safety_level else ""
        target_safety = target.safety_level.upper() if target.safety_level else ""
        
        if "ASIL D" in target_safety or "ASIL C" in target_safety:
            # Increase complexity for high safety components
            if complexity == "MEDIUM":
                complexity = "HIGH"
                
        if "ASIL A" in source_safety or "QM" in source_safety:
            # Decrease complexity for low safety components
            if complexity == "HIGH":
                complexity = "MEDIUM"
                
        # Adjust based on interfaces
        source_interfaces = source.interfaces or []
        if isinstance(source_interfaces, str):
            source_interfaces = source_interfaces.split("|")
            
        target_interfaces = target.interfaces or []
        if isinstance(target_interfaces, str):
            target_interfaces = target_interfaces.split("|")
            
        # Check for common insecure interfaces
        insecure_interfaces = ["http", "ftp", "telnet", "mqtt", "bluetooth"]
        if any(i.lower() in str(source_interfaces).lower() for i in insecure_interfaces) or \
           any(i.lower() in str(target_interfaces).lower() for i in insecure_interfaces):
            # Decrease complexity for insecure interfaces
            if complexity == "HIGH":
                complexity = "MEDIUM"
            elif complexity == "MEDIUM":
                complexity = "LOW"
                
        return complexity
        
    def _generate_paths(
        self,
        component_graph: nx.DiGraph,
        entry_points: List[Component],
        targets: List[Component],
        analysis_id: str,
        scope_id: Optional[str] = None,
        max_depth: int = 5
    ) -> List[AttackPath]:
        """
        Generate attack paths between entry points and targets.
        
        Uses graph algorithms to find paths and then creates AttackPath objects.
        """
        attack_paths = []
        
        # For each entry point and target pair, find possible paths
        for entry_point in entry_points:
            for target in targets:
                entry_id = entry_point.component_id
                target_id = target.component_id
                
                if entry_id == target_id:
                    continue  # Skip if entry point is the target
                
                # Find all simple paths up to max_depth
                try:
                    paths = list(nx.all_simple_paths(
                        component_graph, 
                        source=entry_id, 
                        target=target_id,
                        cutoff=max_depth
                    ))
                except nx.NetworkXError:
                    # Handle case where entry and target are not connected
                    continue
                    
                if not paths:
                    continue
                    
                # Create attack paths from graph paths
                for i, path_nodes in enumerate(paths):
                    # Skip paths that are too short (direct connections without intermediaries)
                    if len(path_nodes) < 3 and len(paths) > 5:  # Only skip short paths if we have many paths
                        continue
                        
                    # Calculate path characteristics
                    path_type = self._determine_path_type(component_graph, path_nodes)
                    complexity = self._calculate_path_complexity(component_graph, path_nodes)
                    success_likelihood = self._calculate_success_likelihood(component_graph, path_nodes)
                    impact = self._calculate_impact(target)
                    risk_score = self._calculate_risk_score(success_likelihood, impact)
                    
                    # Create path name and description
                    name = f"Attack Path {entry_point.name} → {target.name} ({len(path_nodes)-2} hops)"
                    description = f"Attack path from {entry_point.name} to {target.name} via "
                    if len(path_nodes) > 2:
                        intermediates = [component_graph.nodes[n]['name'] for n in path_nodes[1:-1]]
                        description += ", ".join(intermediates)
                    else:
                        description += "direct connection"
                        
                    # Create a new AttackPath object
                    path_id = f"path_{uuid.uuid4().hex}"
                    path = AttackPath(
                        path_id=path_id,
                        analysis_id=analysis_id,
                        scope_id=scope_id,
                        name=name,
                        description=description,
                        path_type=path_type,
                        complexity=complexity,
                        entry_point_id=entry_id,
                        target_id=target_id,
                        success_likelihood=success_likelihood,
                        impact=impact,
                        risk_score=risk_score
                    )
                    
                    # Create steps for this path
                    for j, node_id in enumerate(path_nodes):
                        component = self.db.query(Component).filter(Component.component_id == node_id).first()
                        if not component:
                            continue
                            
                        step_type = self._determine_step_type(j, len(path_nodes), component)
                        step_desc = self._create_step_description(j, component, step_type, path_nodes, component_graph)
                        
                        # Determine relevant vulnerabilities and threats
                        # This would normally query the vulnerability database
                        # For demonstration, we're using empty lists
                        vulnerability_ids = []
                        threat_ids = []
                        
                        step = AttackStep(
                            path_id=path_id,
                            component_id=node_id,
                            step_type=step_type,
                            description=step_desc,
                            prerequisites=[],
                            vulnerability_ids=vulnerability_ids,
                            threat_ids=threat_ids,
                            order=j
                        )
                        
                        path.steps.append(step)
                    
                    self.db.add(path)
                    attack_paths.append(path)
        
        if attack_paths:
            self.db.commit()
        
        return attack_paths
        
    def _determine_path_type(self, graph: nx.DiGraph, path_nodes: List[str]) -> str:
        """
        Determine the type of attack path based on its properties.
        """
        if len(path_nodes) <= 2:
            return AttackPathType.DIRECT
            
        # Check for trust boundary crossings
        trust_boundaries_crossed = 0
        for i in range(len(path_nodes)-1):
            src, dst = path_nodes[i], path_nodes[i+1]
            if graph.edges[src, dst].get('trust_boundary', False):
                trust_boundaries_crossed += 1
                
        if trust_boundaries_crossed > 1:
            # If multiple trust boundaries are crossed, it's likely lateral movement
            return AttackPathType.LATERAL
            
        # Check for privilege escalation by comparing trust zones
        source_zone = graph.nodes[path_nodes[0]].get('trust_zone', '')
        target_zone = graph.nodes[path_nodes[-1]].get('trust_zone', '')
        
        # Define trust zone hierarchy
        zone_hierarchy = {
            'untrusted': 0,
            'external': 0,
            'boundary': 1,
            'standard': 2,
            'trusted': 3,
            'critical': 4
        }
        
        source_level = zone_hierarchy.get(source_zone.lower(), 0)
        target_level = zone_hierarchy.get(target_zone.lower(), 0)
        
        if target_level - source_level >= 2:
            return AttackPathType.PRIVILEGE_ESCALATION
            
        # Default to multi-step if it's not direct but doesn't fit other criteria
        return AttackPathType.MULTI_STEP
        
    def _calculate_path_complexity(self, graph: nx.DiGraph, path_nodes: List[str]) -> str:
        """
        Calculate the overall complexity of an attack path.
        """
        # Collect edge complexities
        edge_complexities = []
        for i in range(len(path_nodes)-1):
            src, dst = path_nodes[i], path_nodes[i+1]
            complexity = graph.edges[src, dst].get('complexity', 'MEDIUM')
            edge_complexities.append(complexity)
            
        # Count occurrences of each complexity level
        high_count = edge_complexities.count('HIGH')
        medium_count = edge_complexities.count('MEDIUM')
        low_count = edge_complexities.count('LOW')
        
        # Determine overall complexity
        if high_count > len(edge_complexities) / 2:
            return AttackComplexity.HIGH
        elif low_count > len(edge_complexities) / 2:
            return AttackComplexity.LOW
        else:
            return AttackComplexity.MEDIUM
            
    def _calculate_success_likelihood(self, graph: nx.DiGraph, path_nodes: List[str]) -> float:
        """
        Calculate the likelihood of successfully executing the attack path.
        
        This is inversely related to complexity - harder paths are less likely to succeed.
        """
        complexity = self._calculate_path_complexity(graph, path_nodes)
        
        # Base likelihood based on complexity
        if complexity == AttackComplexity.HIGH:
            base_likelihood = 0.3  # 30% chance of success for high complexity
        elif complexity == AttackComplexity.MEDIUM:
            base_likelihood = 0.6  # 60% chance for medium complexity
        else:
            base_likelihood = 0.9  # 90% chance for low complexity
            
        # Adjust based on path length - longer paths are less likely to succeed
        length_factor = 1.0 - (len(path_nodes) - 2) * 0.05  # -5% per intermediate hop
        length_factor = max(0.5, length_factor)  # Don't go below 50%
        
        # Final likelihood calculation
        likelihood = base_likelihood * length_factor
        
        return round(likelihood, 2)
        
    def _calculate_impact(self, target: Component) -> Dict[str, int]:
        """
        Calculate the impact of compromising the target component.
        
        Impact is calculated across three dimensions:
        - Confidentiality: Impact on data confidentiality
        - Integrity: Impact on data/system integrity
        - Availability: Impact on system availability
        
        Each is rated on a 1-10 scale.
        """
        # Base impact levels
        impact = {
            "confidentiality": 5,
            "integrity": 5,
            "availability": 5
        }
        
        # Adjust based on safety level
        safety_level = target.safety_level.upper() if target.safety_level else ""
        if "ASIL D" in safety_level:
            impact["integrity"] = 10
            impact["availability"] = 10
        elif "ASIL C" in safety_level:
            impact["integrity"] = 9
            impact["availability"] = 9
        elif "ASIL B" in safety_level:
            impact["integrity"] = 7
            impact["availability"] = 7
        elif "ASIL A" in safety_level:
            impact["integrity"] = 6
            impact["availability"] = 6
            
        # Adjust based on trust zone
        trust_zone = target.trust_zone.lower() if target.trust_zone else ""
        if "critical" in trust_zone:
            impact["confidentiality"] = 9
            impact["integrity"] = max(impact["integrity"], 8)
        elif "trusted" in trust_zone:
            impact["confidentiality"] = 7
            
        # Adjust based on data types
        data_types = target.data_types or []
        if isinstance(data_types, str):
            data_types = data_types.split("|")
            
        data_types_str = str(data_types).lower()
        if any(t in data_types_str for t in ["personal", "private", "credential", "key"]):
            impact["confidentiality"] = 10
        if any(t in data_types_str for t in ["control", "command", "safety"]):
            impact["integrity"] = max(impact["integrity"], 9)
            impact["availability"] = max(impact["availability"], 9)
            
        return impact
        
    def _calculate_risk_score(self, likelihood: float, impact: Dict[str, int]) -> float:
        """
        Calculate overall risk score based on likelihood and impact.
        
        Formula: Risk = Likelihood * Max(Impact)
        """
        max_impact = max(impact.values())
        risk_score = likelihood * max_impact
        
        # Round to 1 decimal place
        return round(risk_score, 1)
        
    def _determine_step_type(self, step_index: int, total_steps: int, component: Component) -> str:
        """
        Determine the type of attack step based on its position in the path and component properties.
        """
        if step_index == 0:
            return AttackStepType.INITIAL_ACCESS
            
        if step_index == total_steps - 1:
            return AttackStepType.IMPACT
            
        # For intermediate steps, determine based on component properties
        component_type = component.type.lower() if component.type else ""
        data_types = str(component.data_types).lower() if component.data_types else ""
        trust_zone = component.trust_zone.lower() if component.trust_zone else ""
        
        if "gateway" in component_type or "proxy" in component_type:
            return AttackStepType.LATERAL_MOVEMENT
            
        if "credential" in data_types or "key" in data_types:
            return AttackStepType.CREDENTIAL_ACCESS
            
        if step_index == 1:
            return AttackStepType.EXECUTION
            
        if "critical" in trust_zone and step_index > total_steps // 2:
            return AttackStepType.PRIVILEGE_ESCALATION
            
        # Default for intermediate steps
        return AttackStepType.LATERAL_MOVEMENT
        
    def _create_step_description(self, step_index: int, component: Component, step_type: str, 
                               path_nodes: List[str], graph: nx.DiGraph) -> str:
        """
        Create a descriptive explanation of the attack step.
        """
        component_name = component.name
        component_type = component.type if component.type else "component"
        
        if step_index == 0:
            return f"Initial access via {component_name} ({component_type})"
            
        if step_index == len(path_nodes) - 1:
            return f"Compromise {component_name} ({component_type}) to achieve attack objective"
            
        if step_type == AttackStepType.LATERAL_MOVEMENT:
            prev_name = graph.nodes[path_nodes[step_index-1]].get('name', 'previous component')
            next_name = graph.nodes[path_nodes[step_index+1]].get('name', 'next component')
            return f"Move laterally from {prev_name} to {component_name} to access {next_name}"
            
        if step_type == AttackStepType.PRIVILEGE_ESCALATION:
            return f"Escalate privileges via {component_name} ({component_type})"
            
        if step_type == AttackStepType.CREDENTIAL_ACCESS:
            return f"Extract credentials from {component_name} ({component_type})"
            
        # Default description
        return f"Exploit {component_name} ({component_type}) to continue attack progression"
        
    def _generate_chains(self, paths: List[AttackPath], analysis_id: str, scope_id: Optional[str] = None) -> List[AttackChain]:
        """
        Generate attack chains by combining related attack paths.
        
        Attack chains represent comprehensive attack scenarios that involve multiple paths.
        """
        if not paths:
            return []
            
        attack_chains = []
        
        # Group paths by entry point and target
        entry_target_groups = {}
        for path in paths:
            key = (path.entry_point_id, path.target_id)
            if key not in entry_target_groups:
                entry_target_groups[key] = []
            entry_target_groups[key].append(path)
            
        # Create chains from groups with multiple paths
        # Also look for chains that share components
        component_paths = {}
        for path in paths:
            # Collect all components in the path
            components = [path.entry_point_id, path.target_id]
            components.extend([step.component_id for step in path.steps if step.component_id not in components])
            
            # Add path to each component's list
            for comp_id in components:
                if comp_id not in component_paths:
                    component_paths[comp_id] = []
                component_paths[comp_id].append(path)
        
        # Find groups of paths that share common components
        processed_paths = set()
        for path in paths:
            if path.path_id in processed_paths:
                continue
                
            related_paths = self._find_related_paths(path, component_paths, processed_paths)
            
            # Create a chain if we found related paths
            if len(related_paths) > 1:
                # Identify all entry points and targets
                entry_points = list(set(p.entry_point_id for p in related_paths))
                targets = list(set(p.target_id for p in related_paths))
                
                # Calculate chain properties
                name = f"Attack Chain {len(entry_points)} entry points → {len(targets)} targets"
                description = "Complex attack scenario involving multiple paths"
                attack_goal = self._determine_attack_goal(targets)
                
                # Calculate max complexity and average likelihood
                complexity = max(p.complexity for p in related_paths)
                avg_likelihood = sum(p.success_likelihood for p in related_paths) / len(related_paths)
                
                # Get max impact for each dimension
                impact = {
                    "confidentiality": max(p.impact.get("confidentiality", 0) for p in related_paths),
                    "integrity": max(p.impact.get("integrity", 0) for p in related_paths),
                    "availability": max(p.impact.get("availability", 0) for p in related_paths)
                }
                
                # Calculate risk score
                risk_score = self._calculate_risk_score(avg_likelihood, impact)
                
                # Create and save the chain
                chain = AttackChain(
                    chain_id=f"chain_{uuid.uuid4().hex}",
                    analysis_id=analysis_id,
                    scope_id=scope_id,
                    name=name,
                    description=description,
                    entry_points=entry_points,
                    targets=targets,
                    attack_goal=attack_goal,
                    complexity=complexity,
                    success_likelihood=avg_likelihood,
                    impact=impact,
                    risk_score=risk_score
                )
                
                # Associate paths with chain
                for related_path in related_paths:
                    chain.paths.append(related_path)
                
                self.db.add(chain)
                attack_chains.append(chain)
                
        if attack_chains:
            self.db.commit()
            
        return attack_chains
        
    def _find_related_paths(self, path: AttackPath, component_paths: Dict[str, List[AttackPath]], 
                          processed_paths: Set[str]) -> List[AttackPath]:
        """
        Find paths that are related to the given path by shared components.
        
        This uses a breadth-first search to find connected paths.
        """
        related = [path]
        processed_paths.add(path.path_id)
        
        # Create a queue of paths to process
        queue = [path]
        while queue:
            current_path = queue.pop(0)
            
            # Get all components in the current path
            components = [current_path.entry_point_id, current_path.target_id]
            components.extend([step.component_id for step in current_path.steps])
            
            # Find all paths that share components with current path
            for comp_id in components:
                for related_path in component_paths.get(comp_id, []):
                    if related_path.path_id not in processed_paths:
                        related.append(related_path)
                        processed_paths.add(related_path.path_id)
                        queue.append(related_path)
                        
        return related
        
    def _determine_attack_goal(self, target_ids: List[str]) -> str:
        """
        Determine the overall goal of an attack chain based on target components.
        """
        targets = self.db.query(Component).filter(Component.component_id.in_(target_ids)).all()
        
        # Look for patterns in target types and data
        target_types = [t.type.lower() for t in targets if t.type]
        data_types = []
        for t in targets:
            if t.data_types:
                if isinstance(t.data_types, list):
                    data_types.extend(t.data_types)
                elif isinstance(t.data_types, str):
                    data_types.extend(t.data_types.split("|"))
        
        data_types_str = ",".join(data_types).lower()
        
        if any(t in target_types for t in ["ecu", "controller"]):
            if "brake" in str(target_types) or "steering" in str(target_types):
                return "Safety System Compromise"
            return "Vehicle Control System Compromise"
            
        if "gateway" in str(target_types) or "telematics" in str(target_types):
            return "Network Infrastructure Compromise"
            
        if any(t in data_types_str for t in ["key", "credential", "certificate"]):
            return "Credential Theft"
            
        if any(t in data_types_str for t in ["personal", "user", "owner", "driver"]):
            return "Personal Data Exfiltration"
            
        if any(t in target_types for t in ["sensor", "camera", "lidar", "radar"]):
            return "Sensor Tampering"
            
        # Default goal
        return "Multiple System Compromise"
        
    def _create_analysis_result(self, analysis_id: str, components: List[Component],
                              entry_points: List[Component], targets: List[Component],
                              paths: List[AttackPath], chains: List[AttackChain],
                              scope_id: Optional[str] = None) -> AttackPathAnalysisResult:
        """
        Create an analysis result object from the computed paths and chains.
        """
        # Count high risk paths and chains
        high_risk_paths = sum(1 for p in paths if p.risk_score >= 7.0)
        high_risk_chains = sum(1 for c in chains if c.risk_score >= 7.0)
        
        # Format entry points and targets for the result
        entry_point_info = [
            {
                "component_id": ep.component_id,
                "name": ep.name,
                "type": ep.type,
                "trust_zone": ep.trust_zone
            }
            for ep in entry_points
        ]
        
        target_info = [
            {
                "component_id": t.component_id,
                "name": t.name,
                "type": t.type,
                "safety_level": t.safety_level,
                "trust_zone": t.trust_zone
            }
            for t in targets
        ]
        
        return AttackPathAnalysisResult(
            analysis_id=analysis_id,
            component_count=len(components),
            entry_points=entry_point_info,
            critical_targets=target_info,
            total_paths=len(paths),
            high_risk_paths=high_risk_paths,
            total_chains=len(chains),
            high_risk_chains=high_risk_chains,
            created_at=datetime.now(),
            scope_id=scope_id
        )
        
    async def get_paths(self, skip: int = 0, limit: int = 100, analysis_id: Optional[str] = None) -> List[AttackPath]:
        """
        Get attack paths, optionally filtered by analysis ID.
        """
        query = self.db.query(AttackPath)
        if analysis_id:
            query = query.filter(AttackPath.analysis_id == analysis_id)
            
        return query.offset(skip).limit(limit).all()
        
    async def get_path(self, path_id: str) -> Optional[AttackPath]:
        """
        Get a specific attack path by ID.
        """
        return self.db.query(AttackPath).filter(AttackPath.path_id == path_id).first()
        
    async def get_chains(self, skip: int = 0, limit: int = 100, analysis_id: Optional[str] = None) -> List[AttackChain]:
        """
        Get attack chains, optionally filtered by analysis ID.
        """
        query = self.db.query(AttackChain)
        if analysis_id:
            query = query.filter(AttackChain.analysis_id == analysis_id)
            
        return query.offset(skip).limit(limit).all()
        
    async def get_chain(self, chain_id: str) -> Optional[AttackChain]:
        """
        Get a specific attack chain by ID.
        """
        return self.db.query(AttackChain).filter(AttackChain.chain_id == chain_id).first()
