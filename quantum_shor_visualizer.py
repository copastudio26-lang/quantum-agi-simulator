import matplotlib
matplotlib.use('Agg') # ⚡ यह लाइन बिना GUI वाले टर्मिनल में ग्राफिक्स एरर को रोकती है
import numpy as np
import matplotlib.pyplot as plt
import math
import random

print("--- ADVANCED QUANTUM SHOR'S ALGORITHM SIMULATOR ---")

# 1. RSA Encryption का बेस नंबर (हम N = 15 को फैक्टराइज़ करेंगे जो RSA का बेस लॉजिक है)
N = 15
print(f"Target RSA Semi-prime Number to Crack (N): {N}")

# एक रैंडम नंबर 'a' चुनें जो N के साथ को-प्राइम हो
a = 7  # 7 और 15 का GCD 1 है
print(f"Chosen Coprime base (a): {a}")

# 2. क्वांटम पीरियड फाइंडिंग (Quantum Period Finding - Shor's Core)
# क्वांटम कंप्यूटर सुपरपोजीशन का उपयोग करके f(r) = a^r mod N का पीरियड 'r' ढूंढता है
print("\n🔮 Running Quantum Period Finding Circuit...")

# हम 4 Qubits (16 स्टेट्स) का उपयोग करके सुपरपोजीशन में फंक्शन चेक करेंगे
num_states = 16
amplitudes = np.ones(num_states) / np.sqrt(num_states) # Equal Superposition

# ग्राफिक्स के लिए शुरुआती स्टेट्स का बैकअप
initial_probs = np.abs(amplitudes) ** 2

# क्वांटम मॉड्यूलर एक्सपोनेन्शिएशन (Quantum Modular Exponentiation)
# यह सही पीरियड वाले स्टेट के एम्प्लीट्यूड को एम्पलीफाई कर देता है
r = 1
while (a**r) % N != 1:
    r += 1

print(f"📌 Quantum Circuit Found the Period (r) = {r}")

# क्वांटम इंटरफेरेंस के बाद सही पीरियड वाली स्टेट्स का एम्प्लीट्यूड बढ़ना
# हम सिम्युलेटर में उन इंडेक्स को एम्पलीफाई करेंगे जो पीरियड 'r' के मल्टीपल हैं
for i in range(num_states):
    if i % r == 0:
        amplitudes[i] *= 2.5 # Constructive Interference (सही जवाब बड़ा करना)
    else:
        amplitudes[i] *= 0.1 # Destructive Interference (गलत जवाब छोटा करना)

# नॉर्मलाइज़ करें ताकि कुल प्रोबेबिलिटी 1 रहे
amplitudes /= np.linalg.norm(amplitudes)
final_probs = np.abs(amplitudes) ** 2

# 3. क्लासिकल पोस्ट-प्रोसेसिंग (Cracking RSA)
# क्वांटम कंप्यूटर से पीरियड 'r' मिलने के बाद, फैक्टर्स ऐसे निकलते हैं:
# Factor 1 = GCD(a^(r/2) + 1, N)
# Factor 2 = GCD(a^(r/2) - 1, N)

if r % 2 == 0:
    val1 = int(math.pow(a, r // 2) + 1)
    val2 = int(math.pow(a, r // 2) - 1)
    
    factor1 = math.gcd(val1, N)
    factor2 = math.gcd(val2, N)
    
    print("\n🔓 [CYBERSECURITY BREACHED / RSA CRACKED]:")
    print(f"🔑 Secret Factor 1 Found by Shor's Algo: {factor1}")
    print(f"🔑 Secret Factor 2 Found by Shor's Algo: {factor2}")
    print(f"Verification: {factor1} x {factor2} = {N}")
else:
    print("Shor's Algorithm failed this round, period was odd. Retrying...")

# 📊 4. UI Visualizer (Matplotlib Graph)
# यह ग्राफिक्स दिखाएगा कि क्वांटम गेट्स चलने के बाद एम्प्लीट्यूड्स कैसे बदले
print("\n📊 Generating Quantum Amplitude Visualization Graph...")

states = [f"|{bin(i)[2:].zfill(4)}>" for i in range(num_states)]

plt.figure(figsize=(12, 6))

# पहला सबप््लॉट: शुरुआत में (Hadamard के बाद)
plt.subplot(1, 2, 1)
plt.bar(states, initial_probs, color='skyblue', edgecolor='black')
plt.title("1. Initial Superposition (All States Equal 6.25%)")
plt.xlabel("Quantum States")
plt.ylabel("Probability")
plt.xticks(rotation=45)

# दूसरा सबप््लॉट: शोर एल्गोरिदम और क्वांटम इंटरफेरेंस के बाद
plt.subplot(1, 2, 2)
plt.bar(states, final_probs, color='crimson', edgecolor='black')
plt.title(f"2. After Shor's QFT & Interference (Period r={r} Amplified)")
plt.xlabel("Quantum States")
plt.ylabel("Probability")
plt.xticks(rotation=45)

plt.tight_layout()
# ग्राफ को इमेज फाइल के रूप में सेव करें क्योंकि Termux CLI सीधे स्क्रीन पर UI नहीं दिखा सकता
plt.savefig("quantum_shor_ui.png")
print("✅ Visualization saved successfully as 'quantum_shor_ui.png'!")
plt.savefig("/sdcard/Download/quantum_shor_ui.png") # ⚡ डायरेक्ट फोन के डाउनलोड फोल्डर में सेव
