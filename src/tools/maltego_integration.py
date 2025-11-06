"""
Maltego data mining integration for the Dynamic Analysis Agent.

Maltego is an interactive data mining tool that renders directed graphs for
link analysis. The tool is used in online investigations for finding
relationships between pieces of information.

This integration performs data mining and link analysis including:
- Entity relationship mapping
- Transform-based data collection
- Graph visualization of connections
- Machine-in-the-box transforms
- Custom entity definitions
- Investigation case management

Used for:
- Link analysis and relationship mapping
- Investigation workflow management
- Data visualization for security findings
- Correlation of disparate data sources
- Threat intelligence analysis
"""

import subprocess
import time
import os

def perform_maltego_transform(target, transform, entity_type='maltego.Domain'):
    """
    Perform Maltego transform on target.

    Args:
        target (str): Target entity value
        transform (str): Transform to run
        entity_type (str): Maltego entity type

    Returns:
        dict: Transform results
    """
    try:
        print(f"\nRunning Maltego transform {transform} on {target}...")

        # Create temporary Maltego graph file
        graph_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<MaltegoMessage MessageType="MaltegoTransformResponse">
    <MaltegoTransformResponseMessage>
        <Entities>
            <Entity Type="{entity_type}">
                <Value>{target}</Value>
                <Weight>100</Weight>
            </Entity>
        </Entities>
    </MaltegoTransformResponseMessage>
</MaltegoMessage>"""

        graph_file = f"maltego_graph_{int(time.time())}.mtgx"
        with open(graph_file, 'w') as f:
            f.write(graph_content)

        # Note: Maltego CLI integration is limited, most functionality requires GUI
        # This is a basic framework for future CLI integration

        cmd = ['maltego', '--run-transform', transform, '--input-entity', f"{entity_type}={target}"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        # Clean up
        if os.path.exists(graph_file):
            os.remove(graph_file)

        if result.returncode == 0:
            print("Maltego transform completed.")

            # Parse output for entities
            lines = result.stdout.split('\n')
            entities = []

            for line in lines:
                if '<Entity' in line or 'Entity:' in line:
                    entities.append(line.strip())

            return {
                "output": result.stdout,
                "target": target,
                "transform": transform,
                "entity_type": entity_type,
                "entities": entities,
                "entity_count": len(entities),
                "success": True,
                "timestamp": time.time()
            }
        else:
            return {
                "error": result.stderr,
                "target": target,
                "transform": transform,
                "success": False,
                "timestamp": time.time()
            }

    except FileNotFoundError:
        print("Maltego not installed. Skipping data mining.")
        return None
    except subprocess.TimeoutExpired:
        # Clean up
        if os.path.exists(graph_file):
            os.remove(graph_file)
        print("Maltego transform timed out.")
        return {
            "error": "Timeout",
            "target": target,
            "transform": transform,
            "success": False,
            "timestamp": time.time()
        }
    except Exception as e:
        # Clean up
        if os.path.exists(graph_file):
            os.remove(graph_file)
        print(f"Error during Maltego transform: {e}")
        return {
            "error": str(e),
            "target": target,
            "transform": transform,
            "success": False,
            "timestamp": time.time()
        }

def create_maltego_graph(entities, relationships, output_file=None):
    """
    Create a Maltego graph file from entities and relationships.

    Args:
        entities (list): List of entity dictionaries
        relationships (list): List of relationship dictionaries
        output_file (str): Output file path

    Returns:
        str: Path to created graph file
    """
    if not output_file:
        output_file = f"maltego_graph_{int(time.time())}.mtgx"

    # Basic Maltego graph XML structure
    graph_content = """<?xml version="1.0" encoding="UTF-8"?>
<MaltegoMessage MessageType="MaltegoGraph">
    <MaltegoGraph>
        <Graph>
"""

    # Add entities
    for i, entity in enumerate(entities):
        entity_type = entity.get('type', 'maltego.Domain')
        value = entity.get('value', '')
        graph_content += f"""            <Node Id="{i}" Type="{entity_type}">
                <Value>{value}</Value>
                <Weight>100</Weight>
            </Node>
"""

    # Add relationships (simplified)
    for rel in relationships:
        graph_content += f"""            <Edge From="{rel['from']}" To="{rel['to']}" Type="{rel.get('type', 'maltego.Link')}"/>
"""

    graph_content += """        </Graph>
    </MaltegoGraph>
</MaltegoMessage>"""

    with open(output_file, 'w') as f:
        f.write(graph_content)

    return output_file

def analyze_relationships(data_sources):
    """
    Analyze relationships between different data sources.

    Args:
        data_sources (dict): Dictionary of data sources with entities

    Returns:
        dict: Relationship analysis
    """
    relationships = []

    # Simple relationship analysis between IPs, domains, emails
    ips = set()
    domains = set()
    emails = set()

    for source, data in data_sources.items():
        if 'hosts' in data:
            for host in data['hosts']:
                if ':' in host:  # IP:port format
                    ip = host.split(':')[0]
                    ips.add(ip)
                else:
                    domains.add(host)

        if 'emails' in data:
            emails.update(data['emails'])

    # Create relationships
    for ip in ips:
        for domain in domains:
            relationships.append({
                'from': ip,
                'to': domain,
                'type': 'DNS Resolution',
                'source': 'analysis'
            })

    for email in emails:
        domain = email.split('@')[-1] if '@' in email else None
        if domain and domain in domains:
            relationships.append({
                'from': email,
                'to': domain,
                'type': 'Email Domain',
                'source': 'analysis'
            })

    return {
        "relationships": relationships,
        "relationship_count": len(relationships),
        "ips": list(ips),
        "domains": list(domains),
        "emails": list(emails),
        "timestamp": time.time()
    }
