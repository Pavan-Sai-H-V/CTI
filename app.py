from flask import Flask, request, render_template, jsonify
from blockchain import Blockchain
from ml_model import classify_threat
import json
import os
from datetime import datetime

app = Flask(__name__)
blockchain = Blockchain()

DATA_FILE = 'data/threats.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/history')
def history():
    data = load_data()
    # Filter out cleared threats and sort by timestamp
    data = [threat for threat in data if not threat.get('cleared', False)]
    data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return render_template('history.html', threats=data)

@app.route('/submit', methods=['POST'])
def submit():
    content = request.json['threat']
    prediction = classify_threat(content)
    
    # Extract primary prediction and confidence scores
    category = prediction['primary_prediction']
    confidence_scores = prediction['confidence_scores']
    
    block = blockchain.add_block({
        "threat": content, 
        "category": category,
        "confidence_scores": confidence_scores,
        "timestamp": datetime.now().isoformat()
    })
    
    data = load_data()
    data.append({
        "threat": content,
        "category": category,
        "confidence_scores": confidence_scores,
        "hash": block.hash,
        "timestamp": datetime.now().isoformat(),
        "cleared": False
    })
    save_data(data)
    return jsonify({
        "message": "Threat added", 
        "category": category,
        "confidence_scores": confidence_scores,
        "hash": block.hash
    })

@app.route('/clear/<hash>', methods=['POST'])
def clear_threat(hash):
    data = load_data()
    for threat in data:
        if threat['hash'] == hash:
            threat['cleared'] = True
            break
    save_data(data)
    return jsonify({"message": "Threat cleared"})

@app.route('/threats')
def threats():
    data = load_data()
    # Filter out cleared threats
    data = [threat for threat in data if not threat.get('cleared', False)]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
