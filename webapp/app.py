"""
Flask Web Application for Codemeta Generator
Provides a web interface to generate and edit codemeta.json files from GitHub repositories
"""

import json
import subprocess
import sys
import os
import re
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from urllib.parse import urlparse
import time

app = Flask(__name__)

# Get the root directory of the codemeta generator
ROOT_DIR = Path(__file__).parent.parent
CODEMETA_SCRIPT = ROOT_DIR / "codemeta_gen.py"


def validate_github_url(url):
    """Validate that the URL is a valid GitHub repository URL"""
    if not url:
        return False, "URL is required"
    
    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"
    
    # Check if it's a GitHub URL
    if parsed.netloc not in ['github.com', 'www.github.com']:
        return False, "URL must be a GitHub repository"
    
    # Check if it has a valid path (owner/repo)
    path_parts = [p for p in parsed.path.split('/') if p]
    if len(path_parts) < 2:
        return False, "URL must be in format: https://github.com/owner/repo"
    
    return True, None


def stream_codemeta_generation(github_url):
    """
    Execute the codemeta generator and stream output in real-time
    Yields JSON-formatted events for Server-Sent Events
    """
    try:
        # Validate URL
        valid, error = validate_github_url(github_url)
        if not valid:
            yield f"data: {json.dumps({'type': 'error', 'message': error})}\n\n"
            return
        
        # Send start event
        yield f"data: {json.dumps({'type': 'start', 'message': 'Starting codemeta generation...'})}\n\n"
        
        # Execute the Python script
        process = subprocess.Popen(
            [sys.executable, str(CODEMETA_SCRIPT), github_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=str(ROOT_DIR)
        )
        
        # Stream output line by line
        for line in iter(process.stdout.readline, ''):
            if line:
                yield f"data: {json.dumps({'type': 'output', 'message': line.rstrip()})}\n\n"
        
        # Wait for process to complete
        return_code = process.wait()
        
        if return_code == 0:
            # Read the generated codemeta.json
            codemeta_path = ROOT_DIR / "codemeta.json"
            if codemeta_path.exists():
                with open(codemeta_path, 'r') as f:
                    codemeta_data = json.load(f)
                
                yield f"data: {json.dumps({'type': 'complete', 'codemeta': codemeta_data})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': 'codemeta.json file not found'})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Process exited with code {return_code}'})}\n\n"
    
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def generate():
    """
    API endpoint to generate codemeta.json from a GitHub repository
    Streams output in real-time using Server-Sent Events
    """
    data = request.get_json()
    github_url = data.get('github_url', '').strip()
    
    return Response(
        stream_with_context(stream_codemeta_generation(github_url)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@app.route('/api/export', methods=['POST'])
def export():
    """
    API endpoint to export the edited codemeta.json
    """
    data = request.get_json()
    codemeta_data = data.get('codemeta', {})
    
    return jsonify({
        'success': True,
        'codemeta': codemeta_data
    })


if __name__ == '__main__':
    # Run the Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
