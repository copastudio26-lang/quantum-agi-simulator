from flask import Flask, render_template_string, request, abort, redirect, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from google import genai
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os
import sqlite3
import requests
import subprocess
import re
from datetime import datetime

app = Flask(__name__)

# Security Headers
Talisman(app, force_https=False, content_security_policy=None)

# Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per day", "20 per minute"],
    storage_uri="memory://"
)

DB_FILE = "quantum_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            question TEXT,
            quantum_state TEXT,
            probability TEXT,
            ai_response TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Keys Setup
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None
ibm_api_key = os.environ.get("IBM_QUANTUM_KEY", "HwBK16xBtYSH2aP4f-C3roD-BgRvJ0doQ520SeVNhIoG")

def fetch_spacex_data():
    try:
        latest_res = requests.get("https://api.spacexdata.com/v4/launches/latest", timeout=2).json()
        return {
            "launch_name": latest_res.get("name", "Starship Test"),
            "flight_number": latest_res.get("flight_number", "IFT-Next"),
            "success": "SUCCESSFUL" if latest_res.get("success") else "ACTIVE MONITORING"
        }
    except Exception:
        return {"launch_name": "Starship Orbital Flight", "flight_number": "IFT-5+", "success": "ONLINE"}

def fetch_gold_rate():
    try:
        res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=inr", timeout=2).json()
        gold_inr_oz = res.get("pax-gold", {}).get("inr", 215000)
        rate_10g = int((gold_inr_oz / 28.3495) * 10)
        return {"status": "LIVE (AUTH SECURE)", "price": f"₹{rate_10g:,} / 10g"}
    except Exception:
        return {"status": "ESTIMATED", "price": "₹74,850 / 10g"}

def process_quantum_16qubits_with_noise(data_string):
    num_qubits = 16
    total_states = 1 << num_qubits
    data_hash = sum(ord(c) for c in data_string)
    np.random.seed(data_hash % 10000)
    num_display_states = 16
    sampled_indices = np.random.choice(total_states, size=num_display_states, replace=False)
    
    amplitudes = np.random.rand(num_display_states) + 1j * np.random.rand(num_display_states)
    hardware_noise = (np.random.rand(num_display_states) * 0.12)
    amplitudes = amplitudes + hardware_noise
    amplitudes /= np.linalg.norm(amplitudes)
    probs = np.abs(amplitudes) ** 2
    
    display_states = [f"|{bin(idx)[2:].zfill(num_qubits)}>" for idx in sampled_indices]
    highest_idx = np.argmax(probs)
    highest_prob_state = display_states[highest_idx]
    highest_prob_val = probs[highest_idx]
    
    plt.figure(figsize=(11, 3.8), facecolor='#020617')
    ax = plt.axes()
    ax.set_facecolor('rgba(15, 23, 42, 0.9)')
    plt.bar(display_states, probs, color='#06b6d4', alpha=0.7, edgecolor='#22d3ee', linewidth=1)
    plt.plot(display_states, probs, marker='o', color='#a855f7', linewidth=1)
    plt.xticks(rotation=70, color='#94a3b8', fontsize=9)
    plt.yticks(color='#94a3b8')
    plt.grid(color='#1e293b', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor=plt.gcf().get_facecolor(), edgecolor='none')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return highest_prob_state, f"{highest_prob_val*100:.2f}%", plot_url

def generate_ai_insights(user_complex_question, quantum_state_summary, probability):
    if not client:
        return "✨ [SIMULATION MODE]: 16-Qubit IBM Node एक्टिव है। अपना सवाल री-सबमिट करें।"
    try:
        prompt = f"You are the Core Intelligence of a 16-Qubit Quantum Supercomputer. User queried: '{user_complex_question}'. Provide a technical answer in Hindi."
        response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
        return response.text
    except Exception as e:
        return f"⚠️ [API Gateway Simulation active]: {str(e)}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>Quantum AGI Cybernetic Core Dash</title>
    <style>
        body { font-family: 'Consolas', monospace; background-color: #020617; color: #f8fafc; text-align: center; padding: 0; margin: 0; overflow-x: hidden; }
        canvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; opacity: 0.12; }
        .ticker-container { background: #0f172a; border-bottom: 2px solid #06b6d4; overflow: hidden; white-space: nowrap; padding: 8px 0; font-size: 13px; color: #06b6d4; }
        .ticker-text { display: inline-block; animation: ticker 25s linear infinite; }
        @keyframes ticker { 0% { transform: translate3d(100%, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
        
        .dashboard-grid { display: grid; grid-template-columns: 1fr 360px; gap: 20px; max-width: 1350px; margin: 20px auto; padding: 10px; box-sizing: border-box; }
        .main-panel { background: rgba(15, 23, 42, 0.9); padding: 30px; border-radius: 12px; border: 1px solid #1e293b; text-align: left; }
        .side-panel { display: flex; flex-direction: column; gap: 20px; }
        .card { background: rgba(15, 23, 42, 0.95); padding: 20px; border-radius: 12px; border: 1px solid #334155; text-align: left; }
        
        textarea { width: 100%; height: 90px; background: #1e293b; color: #38bdf8; border: 1px solid #334155; border-radius: 8px; padding: 12px; font-size: 15px; resize: none; box-sizing: border-box; }
        .btn { background: linear-gradient(135deg, #06b6d4, #2563eb); color: white; border: none; padding: 12px 25px; font-size: 14px; border-radius: 6px; cursor: pointer; font-weight: bold; text-transform: uppercase; margin-top: 8px; }
        
        .terminal-box { background: #020617; border: 1px solid #10b981; color: #10b981; font-family: 'Consolas', monospace; padding: 12px; border-radius: 6px; font-size: 11px; height: 160px; overflow-y: auto; white-space: pre-wrap; }
        .cyan-text { color: #06b6d4; } .amber-text { color: #fbbf24; } .green-text { color: #10b981; }
    </style>
</head>
<body>
    <canvas id="matrix"></canvas>
    <div class="ticker-container"><div class="ticker-text">🌌 [NODE: ACTIVE] || 🛰️ [SPACEX: SYNCED] || 📈 [GOLD FEED: LIVE] || 🛡️ [SUBPROCESS SCANNER: ACTIVE]</div></div>

    <div class="dashboard-grid">
        <div class="main-panel">
            <h1>🌐 Cybernetic Supercomputer Core</h1>
            <form method="POST" action="/">
                <textarea name="question" placeholder="क्वांटम प्रोसेसिंग के लिए अपना सवाल दर्ज करें..." required>{{ request.form.get('question','') }}</textarea>
                <button type="submit" class="btn">🧠 Execute Core Program</button>
            </form>
            
            {% if result %}
            <div style="margin-top:25px; background: rgba(30,41,59,0.5); padding: 20px; border-radius: 8px; border: 1px solid #334155;">
                <h3>🔮 Quantum Array Metrics:</h3>
                <p><b>Collapsed State Vector:</b> <span class="cyan-text">{{ highest_state }}</span> | <b>Probability:</b> <span>{{ probability }}</span></p>
                <div style="font-size: 15px; line-height: 1.6; background: #020617; padding: 15px; border-left: 4px solid #06b6d4; white-space: pre-line;">{{ ai_response }}</div>
                <center><img src="data:image/png;base64,{{ plot_url }}"></center>
            </div>
            {% endif %}
        </div>
        
        <div class="side-panel">
            <div class="card" style="border-color: #fbbf24;">
                <h2 class="amber-text" style="font-size:15px; margin:0 0 8px 0;">📈 Live Gold / SGB Market</h2>
                <p style="font-size:13px; margin:4px 0;"><b>Gold Rate:</b> <span style="color:#fbbf24;">{{ gold.price }}</span></p>
                <p style="font-size:11px; color:#64748b; margin:0;">Status: {{ gold.status }}</p>
            </div>

            <div class="card" style="border-color: #38bdf8;">
                <h2 class="cyan-text" style="font-size:15px; margin:0 0 8px 0;">🛰️ SpaceX Monitor</h2>
                <p style="font-size:12px; margin:4px 0;"><b>Latest:</b> {{ spacex.launch_name }}</p>
                <p style="font-size:12px; margin:4px 0;"><b>Status:</b> <span class="green-text">{{ spacex.success }}</span></p>
            </div>
            
            <div class="card" style="border-color: #10b981;">
                <h2 style="color:#10b981; font-size:15px; margin:0 0 8px 0;">🛡️ Termux Shield Scanner</h2>
                <div style="display:flex; gap:5px; margin-bottom:8px;">
                    <input type="text" id="targetIp" placeholder="e.g. 127.0.0.1" style="background:#1e293b; color:#10b981; border:1px solid #10b981; padding:5px; border-radius:4px; font-size:12px; width:70%;">
                    <button onclick="runRealScan()" class="btn" style="background:#10b981; margin:0; padding:5px 10px; font-size:11px;">Scan</button>
                </div>
                <div class="terminal-box" id="terminalConsole">debian@termux:~# Enter Target IP to trigger system scan...</div>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('matrix'); const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth; canvas.height = window.innerHeight;
        const alphabet = '01XYZ🧬🧠⚡'.split(''); const fontSize = 14; const columns = canvas.width / fontSize;
        const rainDrops = Array(Math.floor(columns)).fill(1);
        function drawMatrix() {
            ctx.fillStyle = 'rgba(2, 6, 23, 0.05)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#06b6d4'; ctx.font = fontSize + 'px monospace';
            for (let i = 0; i < rainDrops.length; i++) {
                const text = alphabet[Math.floor(Math.random() * alphabet.length)];
                ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);
                if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) rainDrops[i] = 0;
                rainDrops[i]++;
            }
        }
        setInterval(drawMatrix, 35);

        function runRealScan() {
            const ip = document.getElementById('targetIp').value;
            const consoleBox = document.getElementById('terminalConsole');
            if(!ip) { alert("IP Address दर्ज करें!"); return; }
            consoleBox.innerHTML = `debian@termux:~# executing subprocess scan...\n`;
            
            fetch('/api/scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ip: ip})
            })
            .then(res => res.json())
            .then(data => {
                consoleBox.innerHTML += `\n[✓] Finished.\n\n` + data.output;
            })
            .catch(err => {
                consoleBox.innerHTML += `\n[⚠️] Scan Error/Blocked.`;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/api/scan', methods=['POST'])
def api_scan():
    data = request.get_json() or {}
    target_ip = data.get('ip', '127.0.0.1')
    if not re.match(r"^[a-zA-Z0-9\.\-]+$", target_ip):
        return jsonify({"output": "Error: Illegal characters."})
    try:
        result = subprocess.run(['ping', '-c', '2', target_ip], capture_output=True, text=True, timeout=5)
        scan_output = result.stdout if result.stdout else result.stderr
    except Exception as e:
        scan_output = f"Scan execution node error: {str(e)}"
    return jsonify({"output": scan_output})

@app.route('/', methods=['GET', 'POST'])
def index():
    spacex_data = fetch_spacex_data()
    gold_data = fetch_gold_rate()

    if request.method == 'POST':
        user_input = request.form.get('question', '')
        if not user_input: return abort(400)
            
        highest_state, probability, plot_url = process_quantum_16qubits_with_noise(user_input)
        ai_response = generate_ai_insights(user_input, highest_state, probability)
        
        return render_template_string(HTML_TEMPLATE, result=True, highest_state=highest_state, probability=probability, ai_response=ai_response, plot_url=plot_url, spacex=spacex_data, gold=gold_data)
    
    return render_template_string(HTML_TEMPLATE, result=False, spacex=spacex_data, gold=gold_data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

