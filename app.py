from flask import Flask, jsonify, request, send_file, render_template
from flask_cors import CORS
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from riskmap.risk_manager import RiskManager, Risk
from riskmap.risk_scoring import calculate_score
from riskmap.control_mapper import ControlMapper
from riskmap.register_exporter import export_to_csv, export_to_json
from riskmap.pdf_exporter import export_to_pdf

app = Flask(__name__)
CORS(app)

# Initialize managers
risk_manager = RiskManager()
control_mapper = ControlMapper()


@app.route('/')
def index():
    """Serve the main web UI."""
    return render_template('index.html')


@app.route('/api/risks', methods=['GET'])
def get_risks():
    """Get all risks."""
    risks = risk_manager.list_risks()
    return jsonify([{
        'id': r.id,
        'name': r.name,
        'description': r.description,
        'likelihood': r.likelihood,
        'impact': r.impact,
        'score': r.score,
        'controls': r.controls,
        'treatment': r.treatment,
        'action_items': r.action_items,
        'owner': r.owner,
        'due_date': r.due_date,
        'status': r.status,
        'framework': r.framework
    } for r in risks])


@app.route('/api/risks/<int:risk_id>', methods=['GET'])
def get_risk(risk_id):
    """Get a specific risk by ID."""
    risk = risk_manager.get_risk(risk_id)
    if not risk:
        return jsonify({'error': 'Risk not found'}), 404
    
    return jsonify({
        'id': risk.id,
        'name': risk.name,
        'description': risk.description,
        'likelihood': risk.likelihood,
        'impact': risk.impact,
        'score': risk.score,
        'controls': risk.controls,
        'treatment': risk.treatment,
        'action_items': risk.action_items,
        'owner': risk.owner,
        'due_date': risk.due_date,
        'status': risk.status,
        'framework': risk.framework
    })


@app.route('/api/risks', methods=['POST'])
def add_risk():
    """Add a new risk."""
    data = request.json
    
    # Validate input
    if not data.get('name'):
        return jsonify({'error': 'Risk name is required'}), 400
    framework = data.get('framework', 'soc2')
    risk.controls = control_mapper.map_controls(risk.name, risk.description, framework)
    
    risk_manager.update_risk(risk)
    
    return jsonify({
        'id': risk.id,
        'name': risk.name,
        'description': risk.description,
        'likelihood': risk.likelihood,
        'impact': risk.impact,
        'score': risk.score,
        'controls': risk.controls,
        'treatment': risk.treatment,
        'action_items': risk.action_items,
        'owner': risk.owner,
        'due_date': risk.due_date,
        'status': risk.status,
        'framework': risk.framework
    }), 201


@app.route('/api/risks/<int:risk_id>', methods=['PUT'])
def update_risk(risk_id):
    """Update an existing risk."""
    risk = risk_manager.get_risk(risk_id)
    if not risk:
        return jsonify({'error': 'Risk not found'}), 404
    
    data = request.json
    
    # Update fields
    if 'name' in data:
        risk.name = data['name']
    if 'description' in data:
        risk.description = data['description']
    if 'likelihood' in data:
        risk.likelihood = data['likelihood']
    if 'impact' in data:
        risk.impact = data['impact']
    
    # Update treatment & remediation fields
    if 'treatment' in data:
        risk.treatment = data['treatment']
    if 'action_items' in data:
        risk.action_items = data['action_items']
    if 'owner' in data:
        risk.owner = data['owner']
    if 'due_date' in data:
        risk.due_date = data['due_date']
    if 'status' in data:
        risk.status = data['status']
    if 'framework' in data:
        risk.framework = data['framework']
    
    # Recalculate score
    risk.score = calculate_score(risk.likelihood, risk.impact)
    
    # Remap controls if name or description changed
    if 'name' in data or 'description' in data:
        framework = data.get('framework', 'soc2')
        risk.controls = control_mapper.map_controls(risk.name, risk.description, framework)
    
    risk_manager.update_risk(risk)
    
    return jsonify({
        'id': risk.id,
        'name': risk.name,
        'description': risk.description,
        'likelihood': risk.likelihood,
        'impact': risk.impact,
        'score': risk.score,
        'controls': risk.controls,
        'treatment': risk.treatment,
        'action_items': risk.action_items,
        'owner': risk.owner,
        'due_date': risk.due_date,
        'status': risk.status,
        'framework': risk.framework
    })


@app.route('/api/risks/<int:risk_id>', methods=['DELETE'])
def delete_risk(risk_id):
    """Delete a risk."""
    if risk_manager.delete_risk(risk_id):
        return jsonify({'message': 'Risk deleted successfully'})
    return jsonify({'error': 'Risk not found'}), 404


@app.route('/api/export/<format>', methods=['GET'])
def export_risks(format):
    """Export risks in specified format."""
    risks = risk_manager.list_risks()
    if not risks:
        return jsonify({'error': 'No risks to export'}), 400
    
    filename = f"risk_register.{format}"
    
    try:
        if format == 'csv':
            export_to_csv(risks, filename)
        elif format == 'json':
            export_to_json(risks, filename)
        elif format == 'pdf':
            export_to_pdf(risks, filename)
        else:
            return jsonify({'error': 'Unsupported format'}), 400
        
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get risk statistics."""
    risks = risk_manager.list_risks()
    
    stats = {
        'total': len(risks),
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'by_status': {},
        'by_owner': {},
        'by_framework': {},
        'top_risks': []
    }
    
    # Sort risks by score (descending) for top risks
    sorted_risks = sorted(risks, key=lambda r: r.score, reverse=True)
    stats['top_risks'] = [{
        'id': r.id,
        'name': r.name,
        'score': r.score,
        'status': r.status,
        'owner': r.owner
    } for r in sorted_risks[:5]]
    
    for risk in risks:
        # Severity counts
        score = risk.score
        if score >= 20:
            stats['critical'] += 1
        elif score >= 15:
            stats['high'] += 1
        elif score >= 10:
            stats['medium'] += 1
        else:
            stats['low'] += 1
            
        # Status counts
        status = risk.status or "Open"
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        # Owner counts
        owner = risk.owner or "Unassigned"
        stats['by_owner'][owner] = stats['by_owner'].get(owner, 0) + 1

        # Framework counts
        framework = risk.framework or "soc2"
        stats['by_framework'][framework] = stats['by_framework'].get(framework, 0) + 1
    
    return jsonify(stats)


if __name__ == '__main__':
    print("🚀 RiskMap Web UI starting...")
    print("📊 Access the dashboard at: http://localhost:5000")
    print("Press CTRL+C to stop the server")
    app.run(debug=True, port=5000)
