import requests

# आपकी ज़ूमआई एपीआई की (API Key)
api_key = "4ABD404b-8ff4-47986-f2cb-fe8ceec0a15"

# हेडर सेट करें ताकि सर्वर पहचान सके
headers = {
    "API-KEY": api_key
}

# सर्च क्वेरी: पोर्ट 554 वाले डिवाइसेस
url = "https://api.zoomeye.ai/host/search?query=port:554"

print("[*] ZoomEye डेटाबेस से कनेक्ट हो रहा है...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("\n[+] सफलता! कुछ लाइव पब्लिक होस्ट्स की लिस्ट:\n")
    
    # रिजल्ट्स में से आईपी और पोर्ट प्रिंट करना
    for matches in data.get('matches', [])[:5]: # केवल टॉप 5 रिजल्ट्स देखने के लिए
        ip = matches.get('ip')
        port = matches.get('portinfo', {}).get('port')
        country = matches.get('geoinfo', {}).get('country', {}).get('names', {}).get('en', 'Unknown')
        print(f"IP: {ip}:{port} | Country: {country}")
else:
    print(f"[-] एरर आया! स्टेटस कोड: {response.status_code}")
    print(response.text)
