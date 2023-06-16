from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# Sample data for the gateway list
with open("gateways.json", "r") as f:
    gateways = json.load(f)

@app.route('/api/add', methods=['GET'])
def add_gateway():
    eui = request.args.get('eui')
    name = request.args.get('name')

    eui = eui.lower()
    # Check if the gateway already exists
    
    if eui in gateways:
        return jsonify({'message': 'Gateway already exists'}), 400

    # Add the new gateway to the list
    gateways[eui] = {'name': name, 'active': "true"}
    with open("gateways.json", "w") as f:
        json.dump(gateways, f)

    return jsonify({'message': 'Gateway added successfully'})

@app.route('/api/remove', methods=['GET'])
def remove_gateway():
    eui = request.args.get('eui').lower()

    # Remove the gateway from the list
    if eui in gateways:
        del gateways[eui]
        with open("gateways.json", "w") as f:
            json.dump(gateways, f)
        return jsonify({'message': 'Gateway removed successfully'})
    
    return jsonify({'message': 'Gateway not found'}), 400

@app.route('/api/list-gateway', methods=['GET'])
def list_gateways():
    return jsonify(gateways)

@app.route('/api/gateway-status', methods=['GET'])
def gateway_status():
    eui = request.args.get('eui')
    eui = eui.lower()
    with open("error_metrics.json", "r") as f:
        metrics = json.load(f)
    # Find the gateway in the list
    pl = {}
    if eui in metrics and eui in gateways:
        pl["error"] = metrics[eui]
        pl["name"] = gateways[eui]["name"]
        pl["active"] = gateways[eui]["active"]
        return jsonify(pl)

    return jsonify({'message': 'Gateway not found'})

@app.route('/api/list-all-status', methods=['GET'])
def list_all_status():
    with open("error_metrics.json", "r") as f:
        metrics = json.load(f)
    # Find the gateway in the list
    pl = {}
    for eui, data in gateways.items():
        pl[eui] = {}
        pl[eui]['name'] = data['name']
        pl[eui]['active'] = data['active']
        if (eui in metrics):
            pl[eui]["error"] = metrics[eui]
        else:
            pl[eui]['error'] = [0,0]
    print(pl)
    return jsonify(pl)

    return jsonify({'message': 'Gateway not found'})

@app.route('/api/set_gateway_status', methods=['GET'])
def set_gateway_status(): # either True (active) or False (disabled)
    eui = request.args.get('eui').lower()
    status = request.args.get('status') # get the gateway status
    gateways[eui]['active'] = status

    # activate/disable the gateway
    if eui in gateways:
        with open("gateways.json", "w") as f:
            json.dump(gateways, f)
        message = ""
        if status == "true":
            message = 'Gateway activated successfully'
        else:
            message = 'Gateway diabled successfully'
            
        return jsonify({'message': message})

    return jsonify({'message': 'Gateway not found'})

if __name__ == '__main__':
    app.run(host='45.32.82.27')
