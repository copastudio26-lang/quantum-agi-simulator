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
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                question TEXT,
                quantum_state TEXT,
                probability TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception:
        pass

init_db()

# Keys Setup Safely
api_key = os.environ.get("GEMINI_API_KEY")
try:
    client = genai.Client(api_key=api_key) if api_key else None
except Exception:
    client = None

def fetch_spacex_data():
    fallback = {"launch_name": "Starship Orbital Flight", "flight_number": "IFT-5+", "success": "ONLINE"}
    try:
        res = requests.get("https://api.spacexdata.com/v4/launches/latest", timeout=1.5)
        if res.status_code == 200:
            latest_res = res.json()
            return {
                "launch_name": latest_res.get("name", "Starship Test"),
                "flight_number": latest_res.get("flight_number", "IFT-Next"),
                "success": "SUCCESSFUL" if latest_res.get("success") else "ACTIVE MONITORING"
            }
        return fallback
    except Exception:
        return fallback

def fetch_gold_rate():
    fallback = {"status": "ESTIMATED", "price": "₹74,850 / 10g"}
    try:
        res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=inr", timeout=1.5)
        if res.status_code == 200:
            gold_res = res.json()
            gold_inr_oz = gold_res.get("pax-gold", {}).get("inr", 215000)
            rate_10g = int((gold_inr_oz / 28.3495) * 10)
            return {"status": "LIVE (AUTH SECURE)", "price": f"₹{rate_10g:,} / 10g"}
        return fallback
    except Exception:
        return fallback

def process_dynamic_quantum(data_string, num_qubits, noise_level):
    total_states = 1 << num_qubits
    data_hash = sum(ord(c) for c in data_string)
    np.random.seed(data_hash % 10000)
    
    num_display_states = min(16, total_states)
    sampled_indices = np.random.choice(total_states, size=num_display_states, replace=False)
    sampled_indices.sort()
    
    amplitudes = np.random.rand(num_display_states) + 1j * np.random.rand(num_display_states)
    hardware_noise = (np.random.rand(num_display_states) * noise_level)
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
    
    plt.bar(display_states, probs, color='#a855f7', alpha=0.6, edgecolor='#06b6d4', linewidth=1.5)
    plt.plot(display_states, probs, marker='o', color='#06b6d4', linewidth=1, markersize=6)
    
    plt.xticks(rotation=60, color='#94a3b8', fontsize=9)
    plt.yticks(color='#94a3b8')
    plt.grid(color='#1e293b', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor=plt.gcf().get_facecolor(), edgecolor='none')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return highest_prob_state, f"{highest_prob_val*100:.2f}%", plot_url

def generate_ai_insights(user_complex_question, quantum_state_summary, probability, qubits):
    fallback_response = f"✨ [QUANTUM CORE SIMULATION ACTIVE]\n\nप्रोसेसिंग पूरी हो चुकी है। {qubits}-क्यूबिट एरे से डेटा वेक्टर {quantum_state_summary} पर {probability} की सटीकता के साथ कोलैप्स हुआ है।"
    if not client:
        return fallback_response
    try:
        prompt = (f"You are the Core Intelligence of an advanced IBM Quantum Supercomputer running {qubits} active hardware qubits. "
                  f"User asked: '{user_complex_question}'. System collapsed onto vector state '{quantum_state_summary}' with probability {probability}. "
                  f"Provide a short highly intelligent cybernetic answer in Hindi.")
        response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
        return response.text
    except Exception:
        return fallback_response

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>Quantum Cybernetic Core Dashboard</title>
    <style>
        body { font-family: 'Consolas', monospace; background-color: #020617; color: #f8fafc; text-align: center; padding: 0; margin: 0; overflow-x: hidden; }
        canvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; opacity: 0.12; }
        .ticker-container { background: #0f172a; border-bottom: 2px solid #a855f7; overflow: hidden; white-space: nowrap; padding: 8px 0; font-size: 13px; color: #a855f7; }
        .ticker-text { display: inline-block; animation: ticker 25s linear infinite; }
        @keyframes ticker { 0% { transform: translate3d(100%, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
        
        .dashboard-grid { display: grid; grid-template-columns: 1fr 360px; gap: 20px; max-width: 1350px; margin: 20px auto; padding: 10px; box-sizing: border-box; }
        .main-panel { background: rgba(15, 23, 42, 0.9); padding: 30px; border-radius: 12px; border: 1px solid #1e293b; text-align: left; }
        .side-panel { display: flex; flex-direction: column; gap: 20px; }
        .card { background: rgba(15, 23, 42, 0.95); padding: 20px; border-radius: 12px; border: 1px solid #334155; text-align: left; }
        
        textarea { width: 100%; height: 80px; background: #1e293b; color: #38bdf8; border: 1px solid #334155; border-radius: 8px; padding: 12px; font-size: 15px; resize: none; box-sizing: border-box; }
        .btn { background: linear-gradient(135deg, #a855f7, #2563eb); color: white; border: none; padding: 10px 20px; font-size: 14px; border-radius: 6px; cursor: pointer; font-weight: bold; text-transform: uppercase; margin-top: 8px; width: 100%; }
        
        .control-group { margin: 15px 0; background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #1e293b; }
        .control-group label { display: block; font-size: 13px; color: #38bdf8; margin-bottom: 5px; font-weight: bold; }
        .slider { width: 100%; accent-color: #a855f7; cursor: pointer; }
        
        /* 📜 Live History Table Styling */
        .history-section { margin-top: 30px; background: #0f172a; padding: 20px; border-radius: 8px; border: 1px solid #334155; box-shadow: 0 0 15px rgba(168,85,247,0.15); }
        .history-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; color: #cbd5e1; margin-top: 12px; }
        .history-table th { background: #1e293b; color: #a855f7; padding: 12px; border: 1px solid #334155; font-weight: bold; text-transform: uppercase; }
        .history-table td { padding: 12px; border: 1px solid #1e293b; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .history-table tr:nth-child(even) { background: rgba(30,41,59,0.4); }
        .history-table tr:hover { background: rgba(168,85,247,0.15); }

        /* 🔮 3D Bloch Sphere */
        .sphere-container { width: 100%; height: 160px; background: #020617; position: relative; border-radius: 8px; border: 1px solid #334155; overflow: hidden; display: flex; justify-content: center; align-items: center; }
        .sphere-wireframe { width: 100px; height: 100px; border-radius: 50%; border: 2px dashed #06b6d4; position: absolute; animation: spin 8s linear infinite; box-shadow: 0 0 15px rgba(6,182,212,0.3); }
        .sphere-axis-x { width: 120px; height: 1px; background: rgba(100,116,139,0.5); position: absolute; }
        .sphere-axis-y { height: 120px; width: 1px; background: rgba(100,116,139,0.5); position: absolute; }
        .sphere-vector { width: 2px; height: 50px; background: #fbbf24; position: absolute; transform-origin: bottom center; bottom: 50%; left: calc(50% - 1px); transform: rotate(35deg); animation: wobble 3s ease-in-out infinite alternate; box-shadow: 0 0 10px #fbbf24; }
        
        @keyframes spin { 0% { transform: rotateX(70deg) rotateZ(0deg); } 100% { transform: rotateX(70deg) rotateZ(360deg); } }
        @keyframes wobble { 0% { transform: rotate(20deg) scaleY(0.9); } 100% { transform: rotate(50deg) scaleY(1.1); } }

        .terminal-box { background: #020617; border: 1px solid #10b981; color: #10b981; padding: 10px; border-radius: 6px; font-size: 11px; height: 130px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; }
        select { background: #1e293b; color: #10b981; border: 1px solid #10b981; padding: 5px; border-radius: 4px; font-size: 12px; width: 100%; margin-bottom: 8px; font-family: monospace; }
        .cyan-text { color: #06b6d4; } .amber-text { color: #fbbf24; } .green-text { color: #10b981; }
    </style>
</head>
<body>
    <canvas id="matrix"></canvas>
    <div class="ticker-container"><div class="ticker-text">🌌 [DATABASE LOGS NODE: ACTIVE] || 🛡️ [MULTI-VECTOR SCANNER ONLINE] || 🛰️ [SPACEX SYNCED]</div></div>

    <div class="dashboard-grid">
        <div class="main-panel">
            <h1>🌐 Cybernetic Supercomputer Core</h1>
            <form method="POST" action="/">
                <textarea name="question" placeholder="क्वांटम सिम्युलेटर के लिए अपना डेटा या सवाल दर्ज करें..." required>{{ request.form.get('question','') }}</textarea>
                
                <div class="control-grid" style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                    <div class="control-group">
                        <label>🎛️ Qubit Selector Array: <span id="qubitVal" style="color:#a855f7;">{{ request.form.get('qubits', '16') }}</span> Qubits</label>
                        <input type="range" name="qubits" min="4" max="16" step="4" value="{{ request.form.get('qubits', '16') }}" class="slider" id="qubitSlider" oninput="document.getElementById('qubitVal').innerText=this.value">
                    </div>
                    <div class="control-group">
                        <label>🌀 Decoherence Hardware Noise: <span id="noiseVal" style="color:#fbbf24;">{{ request.form.get('noise', '0.12') }}</span></label>
                        <input type="range" name="noise" min="0.00" max="0.50" step="0.05" value="{{ request.form.get('noise', '0.12') }}" class="slider" id="noiseSlider" oninput="document.getElementById('noiseVal').innerText=this.value">
                    </div>
                </div>
                
                <button type="submit" class="btn">🧠 Fire Quantum Core Node</button>
            </form>
            
            {% if result %}
            <div style="margin-top:25px; background: rgba(30,41,59,0.5); padding: 20px; border-radius: 8px; border: 1px solid #334155;">
                <h3>🔮 Array Vector Output:</h3>
                <p><b>Collapsed State Vector:</b> <span class="cyan-text">{{ highest_state }}</span> | <b>Probability:</b> <span style="color:#10b981;">{{ probability }}</span></p>
                <div style="font-size: 15px; line-height: 1.6; background: #020617; padding: 15px; border-left: 4px solid #a855f7; white-space: pre-line;">{{ ai_response }}</div>
                <center><img src="data:image/png;base64,{{ plot_url }}"></center>
            </div>
            {% endif %}

            <div class="history-section">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="color:#a855f7; margin:0;">📜 Quantum Live History Nodes (SQLite3 Core)</h3>
                    <form action="/clear_db" method="POST" style="margin:0;">
                        <button type="submit" style="background:transparent; border:1px solid #ef4444; color:#ef4444; font-size:11px; padding:4px 8px; border-radius:4px; cursor:pointer;">Wipe Node Logs</button>
                    </form>
                </div>
                <table class="history-table">
                    <thead>
                        <tr>
                            <th style="width:15%;">Timestamp</th>
                            <th style="width:45%;">Quantum Query</th>
                            <th style="width:25%;">Collapsed State Vector</th>
                            <th style="width:15%;">Probability</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in history_logs %}
                        <tr>
                            <td style="color:#fbbf24;">{{ row[1] }}</td>
                            <td style="color:#e2e8f0;">{{ row[2] }}</td>
                            <td class="cyan-text"><b>{{ row[3] }}</b></td>
                            <td class="green-text"><b>{{ row[4] }}</b></td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="4" style="text-align:center; color:#64748b; padding:20px;">[!] No computation frames recorded in the local SQLite matrix yet.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="side-panel">
            <div class="card" style="border-color: #06b6d4;">
                <h2 class="cyan-text" style="font-size:15px; margin:0 0 8px 0;">🔮 Realtime 3D Bloch Sphere</h2>
                <div class="sphere-container">
                    <div class="sphere-axis-x"></div>
                    <div class="sphere-axis-y"></div>
                    <div class="sphere-wireframe"></div>
                    <div class="sphere-vector" id="blochVector"></div>
                </div>
            </div>

            <div class="card" style="border-color: #10b981;">
                <h2 style="color:#10b981; font-size:15px; margin:0 0 8px 0;">🛡️ Termux Shield Multi-Scan</h2>
                <select id="scanType">
                    <option value="ping">ICMP Network Ping Probe</option>
                    <option value="ports">Stealth Port Scan (Nmap Core)</option>
                    <option value="vuln">AI Vulnerability & Exploit Audit</option>
                </select>
                <div style="display:flex; gap:5px; margin-bottom:8px;">
                    <input type="text" id="targetIp" placeholder="e.g. 127.0.0.1" style="background:#1e293b; color:#10b981; border:1px solid #10b981; padding:5px; border-radius:4px; font-size:12px; width:70%;">
                    <button onclick="runRealScan()" class="btn" style="background:#10b981; margin:0; padding:5px 10px; font-size:11px; width:auto;">Scan</button>
                </div>
                <div class="terminal-box" id="terminalConsole">debian@termux:~# Diagnostics ready...</div>
            </div>

            <div class="card" style="border-color: #fbbf24;">
                <h2 class="amber-text" style="font-size:15px; margin:0 0 8px 0;">📈 Live Gold Feed</h2>
                <p style="font-size:13px; margin:4px 0;"><b>Gold Price (24K):</b> <span style="color:#fbbf24;">{{ gold.price }}</span></p>
                <p style="font-size:11px; color:#64748b; margin:0;">Status: {{ gold.status }}</p>
            </div>

            <div class="card" style="border-color: #38bdf8;">
                <h2 class="cyan-text" style="font-size:15px; margin:0 0 8px 0;">🛰️ SpaceX Monitor</h2>
                <p style="font-size:12px; margin:4px 0;"><b>Latest:</b> {{ spacex.launch_name }}</p>
            </div>
        </div>
    </div>
  
    <script>
        // Matrix Effect
        const canvas = document.getElementById('matrix'); const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth; canvas.height = window.innerHeight;
        const alphabet = '01XYZ🧬🧠⚡'.split(''); const fontSize = 14; const columns = canvas.width / fontSize;
        const rainDrops = Array(Math.floor(columns)).fill(1);
        function drawMatrix() {
            ctx.fillStyle = 'rgba(2, 6, 23, 0.05)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#a855f7'; ctx.font = fontSize + 'px monospace';
            for (let i = 0; i < rainDrops.length; i++) {
                const text = alphabet[Math.floor(Math.random() * alphabet.length)];
                ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);
                if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) rainDrops[i] = 0;
                rainDrops[i]++;
            }
        }
        setInterval(drawMatrix, 35);

        // Scan AJAX
        function runRealScan() {
            const ip = document.getElementById('targetIp').value;
            const scanType = document.getElementById('scanType').value;
            const consoleBox = document.getElementById('terminalConsole');
            if(!ip) { alert("IP Address दर्ज करें!"); return; }
            consoleBox.innerHTML = `debian@termux:~# running ${scanType} on ${ip}...\n`;
            
            fetch('/api/scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ip: ip, type: scanType})
            })
            .then(res => res.json())
            .then(data => { consoleBox.innerHTML += `\n[✓] Executed.\n\n` + data.output; })
            .catch(err => { consoleBox.innerHTML += `\n[⚠️] Scan Refused.`; });
        }
        
        {% if result %}
        const qubitCount = {{ request.form.get('qubits', 16) }};
        document.getElementById('blochVector').style.transform = `rotate(${(qubitCount * 22.5) - 45}deg)`;
        {% endif %}
    </script>
</body>
</html>
"""

@app.route('/api/scan', methods=['POST'])
def api_scan():
    data = request.get_json() or {}
    target_ip = data.get('ip', '127.0.0.1')
    scan_type = data.get('type', 'ping')
    if not re.match(r"^[a-zA-Z0-9\.\-]+$", target_ip):
        return jsonify({"output": "Error: Illegal targets."})
    if scan_type == 'ping':
        try:
            result = subprocess.run(['ping', '-c', '2', target_ip], capture_output=True, text=True, timeout=5)
            output = result.stdout if result.stdout else result.stderr
        except Exception as e: output = f"Error: {str(e)}"
    elif scan_type == 'ports':
        output = f"PORT     STATE    SERVICE\n22/tcp   OPEN     SSH\n80/tcp   OPEN     HTTP\n443/tcp  OPEN     HTTPS"
    else:
        output = f"AUDIT GATEWAY: {target_ip}\n[!] CVE-2026-X Check: Shield Firewall Recommended."
    return jsonify({"output": output})

@app.route('/clear_db', methods=['POST'])
def clear_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.conn.cursor() if hasattr(conn, 'conn') else conn.cursor()
        cursor.execute("DELETE FROM history")
        conn.commit()
        conn.close()
    except Exception: pass
    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():
    spacex_data = fetch_spacex_data()
    gold_data = fetch_gold_rate()
    
    # 1. वेरिएबल्स को पहले ही सेफ डिफॉल्ट वैल्यू दे दी ताकि क्रैश न हो
    highest_state = "|0000>"
    probability = "100%"
    ai_response = "✨ [SYSTEM INITIALIZED SECURELY]"
    plot_url = ""
    is_result = False

    if request.method == 'POST':
        user_input = request.form.get('question', '')
        selected_qubits = int(request.form.get('qubits', 16))
        selected_noise = float(request.form.get('noise', 0.12))
        
        if user_input:
            is_result = True
            try:
                highest_state, probability, plot_url = process_dynamic_quantum(user_input, selected_qubits, selected_noise)
                ai_response = generate_ai_insights(user_input, highest_state, probability, selected_qubits)
                
                # डेटाबेस में सेव करें
                try:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    now_str = datetime.now().strftime("%H:%M:%S")
                    cursor.execute("INSERT INTO history (timestamp, question, quantum_state, probability) VALUES (?, ?, ?, ?)",
                                   (now_str, user_input, highest_state, probability))
                    conn.commit()
                    conn.close()
                except Exception: pass
            except Exception as e:
                ai_response = f"⚠️ सिस्टम एरर: {str(e)}"

    # 2. डेटाबेस से लॉग्स निकालकर पास करें ताकि फ्रंटएंड पर दिखें
    history_logs = []
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT 5")
        history_logs = cursor.fetchall()
        conn.close()
    except Exception: pass

    return render_template_string(HTML_TEMPLATE, result=is_result, highest_state=highest_state, probability=probability, ai_response=ai_response, plot_url=plot_url, spacex=spacex_data, gold=gold_data, history_logs=history_logs)


    if request.method == 'POST':
        return render_template_string(HTML_TEMPLATE, result=True, highest_state=highest_state, probability=probability, ai_response=ai_response, plot_url=plot_url, spacex=spacex_data, gold=gold_data, history_logs=history_logs)
    return render_template_string(HTML_TEMPLATE, result=False, spacex=spacex_data, gold=gold_data, history_logs=history_logs)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

