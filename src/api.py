"""
REST API for the Dynamic Analysis Agent.
"""

import threading
import time
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional
import uuid

from .docker_manager import run_docker_container, cleanup_container
from .vulnerability_scanner import test_vulnerabilities
from .tools import (
    start_zap, perform_zap_scan, stop_zap,
    perform_nmap_scan, perform_nikto_scan
)
from .logger import logger
from .config import config

app = Flask(__name__)

# Global scan storage
active_scans: Dict[str, Dict[str, Any]] = {}
scan_results: Dict[str, Dict[str, Any]] = {}

def perform_scan_async(scan_id: str, image: str, port: int = 8080, url: Optional[str] = None):
    """
    Perform scan asynchronously.

    Args:
        scan_id (str): Unique scan identifier
        image (str): Docker image to scan
        port (int): Port to use
        url (str): Custom URL
    """
    try:
        active_scans[scan_id]["status"] = "running"
        logger.info(f"Starting async scan {scan_id} for image {image}")

        base_url = url or f"http://localhost:{port}"

        # Start ZAP
        zap_process = start_zap()

        # Run container
        if not run_docker_container(image, port=port):
            active_scans[scan_id]["status"] = "failed"
            active_scans[scan_id]["error"] = "Failed to start container"
            return

        # Perform tests (simplified version without progress bars for API)
        results = {
            "target": base_url,
            "timestamp": time.time(),
            "vulnerabilities": [],
            "tools": [],
            "summary": {}
        }

        # Test vulnerabilities
        vulnerabilities = test_vulnerabilities(base_url)
        results["vulnerabilities"].extend(vulnerabilities)

        # Run tools
        nmap_results = perform_nmap_scan("localhost", port)
        if nmap_results:
            results["tools"].append({"name": "nmap", "results": nmap_results})

        nikto_results = perform_nikto_scan(base_url)
        if nikto_results:
            results["tools"].append({"name": "nikto", "results": nikto_results})

        zap_results = perform_zap_scan(base_url)
        if zap_results:
            results["tools"].append({"name": "zap", "results": zap_results})

        # Generate summary
        vuln_types = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.get("type", "Unknown")
            vuln_types[vuln_type] = vuln_types.get(vuln_type, 0) + 1

        results["summary"] = {
            "total_vulnerabilities": len(vulnerabilities),
            "vulnerability_types": vuln_types,
            "tools_run": len(results["tools"]),
            "scan_duration": time.time() - results["timestamp"]
        }

        # Store results
        scan_results[scan_id] = results
        active_scans[scan_id]["status"] = "completed"

        # Cleanup
        cleanup_container()

    except Exception as e:
        logger.error(f"Error in async scan {scan_id}: {e}")
        active_scans[scan_id]["status"] = "failed"
        active_scans[scan_id]["error"] = str(e)
    finally:
        stop_zap(zap_process)

@app.route('/api/v1/scans', methods=['POST'])
def create_scan():
    """Create a new scan."""
    data = request.get_json()

    if not data or 'image' not in data:
        return jsonify({'error': 'Missing required field: image'}), 400

    scan_id = str(uuid.uuid4())
    image = data['image']
    port = data.get('port', config.get('docker.default_port', 8080))
    url = data.get('url')

    active_scans[scan_id] = {
        'id': scan_id,
        'image': image,
        'port': port,
        'url': url,
        'status': 'pending',
        'created_at': time.time()
    }

    # Start scan in background thread
    thread = threading.Thread(
        target=perform_scan_async,
        args=(scan_id, image, port, url)
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        'scan_id': scan_id,
        'status': 'pending',
        'message': 'Scan started successfully'
    }), 201

@app.route('/api/v1/scans', methods=['GET'])
def list_scans():
    """List all scans."""
    scans = []
    for scan_id, scan_info in {**active_scans, **scan_results}.items():
        scans.append({
            'id': scan_id,
            'status': scan_info.get('status', 'unknown'),
            'image': scan_info.get('image'),
            'created_at': scan_info.get('created_at', scan_info.get('timestamp')),
            'target': scan_info.get('target')
        })

    return jsonify({'scans': scans})

@app.route('/api/v1/scans/<scan_id>', methods=['GET'])
def get_scan(scan_id):
    """Get scan details and results."""
    if scan_id in scan_results:
        return jsonify(scan_results[scan_id])
    elif scan_id in active_scans:
        return jsonify({
            'id': scan_id,
            'status': active_scans[scan_id]['status'],
            'image': active_scans[scan_id]['image'],
            'created_at': active_scans[scan_id]['created_at'],
            'error': active_scans[scan_id].get('error')
        })
    else:
        return jsonify({'error': 'Scan not found'}), 404

@app.route('/api/v1/scans/<scan_id>', methods=['DELETE'])
def delete_scan(scan_id):
    """Delete a scan."""
    if scan_id in scan_results:
        del scan_results[scan_id]
        return jsonify({'message': 'Scan deleted successfully'})
    elif scan_id in active_scans:
        # Cancel active scan (simplified - in real implementation, you'd need proper cancellation)
        active_scans[scan_id]['status'] = 'cancelled'
        return jsonify({'message': 'Scan cancelled'})
    else:
        return jsonify({'error': 'Scan not found'}), 404

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0'
    })

@app.route('/api/v1/config', methods=['GET'])
def get_config():
    """Get current configuration (redacted for security)."""
    # Return only non-sensitive config
    safe_config = {
        'docker': config.get('docker', {}),
        'reporting': config.get('reporting', {}),
        'scanning': config.get('scanning', {})
    }
    return jsonify(safe_config)

def run_api(host='0.0.0.0', port=5000, debug=False):
    """
    Run the API server.

    Args:
        host (str): Host to bind to
        port (int): Port to bind to
        debug (bool): Enable debug mode
    """
    logger.info(f"Starting API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    run_api()
