import uuid
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify, send_from_directory

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db =firestore.client()

app = Flask(__name__)


app = Flask(__name__, static_folder=None)

# In-memory data stores (simple for local testing)
REQUESTS = {}
INVENTORY = {
    "A+": 20,
    "A-": 15,
    "B+": 30,
    "B-": 10,
    "O+": 40,
    "O-": 10,
    "AB+": 5,
    "AB-": 5
}


def dt_str():
    pass


# --- Requests API ---
@app.route('/api/requests', methods=['POST'])
def create_request():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    required = ['hospitalId', 'bloodGroup', 'unitsRequired']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing fields"}), 400

    try:
        units = int(data['unitsRequired'])
    except (ValueError, TypeError):
        return jsonify({"error": "unitsRequired must be integer"}), 400

    req_id = str(uuid.uuid4())
    new_request = {
        "id": req_id,
        "hospitalId": data['hospitalId'],
        "bloodGroup": data['bloodGroup'].upper(),
        "unitsRequired": units,
        "status": "pending",
        "requestedAt": dt_str()
    }

    REQUESTS[req_id] = new_request
    return jsonify({"message": "Request submitted", "id": req_id}), 201


@app.route('/api/requests', methods=['GET'])
def list_requests():
    return jsonify(list(REQUESTS.values())), 200


@app.route('/api/requests/<request_id>/approve', methods=['POST'])
def approve_request(request_id):
    req = REQUESTS.get(request_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404
    if req['status'] != 'pending':
        return jsonify({"error": "Request already processed"}), 400
    bg = req['bloodGroup']
    units = req['unitsRequired']
    if INVENTORY.get(bg, 0) < units:
        return jsonify({"error": "Insufficient inventory"}), 400
    INVENTORY[bg] = INVENTORY.get(bg, 0) - units
    req['status'] = 'approved'
    dt_str()
    return jsonify({'message': 'Request approved', 'remainingUnits': INVENTORY[bg]}), 200


@app.route('/api/requests/<request_id>/reject', methods=['POST'])
def reject_request(request_id):
    req = REQUESTS.get(request_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404
    if req['status'] != 'pending':
        return jsonify({"error": "Request already processed"}), 400
    req['status'] = 'rejected'
    dt_str()
    return jsonify({'message': 'Request rejected'}), 200


# --- Inventory API ---
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    return jsonify(INVENTORY), 200


@app.route('/api/inventory/<bg>', methods=['GET'])
def get_inventory_bg(bg):
    bg = bg.upper()
    if bg not in INVENTORY:
        return jsonify({'error': 'Unknown blood group'}), 404
    return jsonify({'bloodGroup': bg, 'unitsAvailable': INVENTORY[bg]}), 200


@app.route('/api/inventory', methods=['POST'])
def set_inventory():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    bg = data.get('bloodGroup')
    units = data.get('unitsAvailable')
    if not bg or units is None:
        return jsonify({'error': 'Missing fields'}), 400
    try:
        units = int(units)
    except (ValueError, TypeError):
        return jsonify({'error': 'unitsAvailable must be integer'}), 400
    bg = bg.upper()
    INVENTORY[bg] = units
    return jsonify({'message': 'Inventory updated', 'bloodGroup': bg, 'unitsAvailable': units}), 200


# --- Static frontend serving ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = str(PROJECT_ROOT / 'frontend')


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_frontend(path):
    # prevent capturing API paths
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    # sanitize path
    return send_from_directory(FRONTEND_DIR, path)


if __name__ == '__main__':
    app.run(debug=True)
