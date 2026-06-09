from flask import Flask, render_template_string, request, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)

# 🛡️ सुरक्षा कवच 1: सुरक्षित हेडर लागू करना
Talisman(app, force_https=False, content_security_policy=None)

# 🛡️ सुरक्षा कवच 2: क्लाउड-फ्रेंडली रेट लिमिटर इनिशियलाइज़ेशन (फिक्स)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per day", "20 per minute"],
    storage_uri="memory://"
)

def process_complex_data(data_string):
    num_states = 16
    data_hash = sum(ord(c) for c in data_string)
    
    np.random.seed(data_hash % 1000)
    amplitudes = np.random.rand(num_states) + 1j * np.random.rand(num_states)
    amplitudes /= np.linalg.norm(amplitudes)
    probs = np.abs(amplitudes) ** 2
    
    states = [f"|{bin(i)[2:].zfill(4)}>" for i in range(num_states)]
    highest_prob_state = states[np.argmax(probs)]
    
    plt.figure(figsize=(10, 4))
    plt.plot(states, probs, marker='o', color='#38bdf8', linewidth=2, markersize=8)
    plt.fill_between(states, probs, color='#38bdf8', alpha=0.2)
    plt.title("Complex Data Encoded into Quantum Superposition Map")
    plt.xticks(rotation=45)
    plt.grid(color='#334155', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return highest_prob_state, plot_url

from google import genai
import os

# Gemini क्लाइंट इनिशियलाइज़ करें (यह पर्यावरण से API की उठाएगा)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_ai_insights(user_complex_question, quantum_state_summary):
    try:
        # यहाँ हम प्रॉम्ट को बहुत ही एडवांस बना रहे हैं
        prompt = (
            f"You are an Advanced AGI Core acting over a Quantum Simulator. "
            f"The user asked this complex question: '{user_complex_question}'. "
            f"The quantum engine processed this and collapsed into the dominant state: '{quantum_state_summary}'. "
            f"Provide a highly sophisticated, technical, and brilliant response in Hindi, analyzing how the quantum state helps resolve their problem."
        )
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ [API Connection Error]: {str(e)}"


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>Quantum AGI & Generative Engine</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #020617; color: #f8fafc; text-align: center; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: #0f172a; padding: 40px; border-radius: 20px; box-shadow: 0 20px 50px rgba(0,0,0,0.7); border: 1px solid #1e293b; }
        h1 { color: #38bdf8; font-size: 2.5rem; }
        textarea { width: 100%; height: 100px; background: #1e293b; color: white; border: 1px solid #334155; border-radius: 10px; padding: 15px; font-size: 16px; resize: none; margin-bottom: 20px; }
        .btn { background: linear-gradient(135deg, #06b6d4, #3b82f6); color: white; border: none; padding: 15px 35px; font-size: 18px; border-radius: 10px; cursor: pointer; font-weight: bold; }
        .result-box { margin-top: 40px; padding: 25px; background: #1e293b; border-radius: 12px; text-align: left; }
        .ai-text { font-size: 18px; line-height: 1.6; color: #e2e8f0; background: #020617; padding: 20px; border-radius: 8px; border-left: 6px solid #10b981; }
        img { max-width: 100%; margin-top: 25px; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Quantum AGI & Generative Cloud Platform</h1>
        <form method="POST">
            <textarea name="question" placeholder="यहाँ अपना कोई भी बड़ा या जटिल सवाल/डेटा लिखें..." required></textarea>
            <br>
            <button type="submit" class="btn">🧠 Process with Quantum AI</button>
        </form>
        {% if result %}
        <div class="result-box">
            <h2>🔮 Quantum Superposition Analysis:</h2>
            <p><b>Dominant Quantum State Collapse:</b> {{ highest_state }}</p>
            <h2>✨ Generative AI New Output:</h2>
            <div class="ai-text">{{ ai_response }}</div>
            <center><img src="data:image/png;base64,{{ plot_url }}"></center>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form.get('question', '')
        if not user_input:
            return abort(400)
        highest_state, plot_url = process_complex_data(user_input)
        ai_response = generate_ai_insights(user_input, highest_state)
        return render_template_string(HTML_TEMPLATE, result=True, highest_state=highest_state, ai_response=ai_response, plot_url=plot_url)
    return render_template_string(HTML_TEMPLATE, result=False)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

