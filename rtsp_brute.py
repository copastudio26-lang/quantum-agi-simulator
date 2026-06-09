import subprocess

ip = "103.11.82.16"
port = "554"

# सबसे कॉमन रास्तों की लिस्ट
paths = [
    "live/ch0", "live/ch1", "live.sdp", "video.mp4", "mpeg4", "h264", 
    "Streaming/channels/1", "cam/realmonitor?channel=1&subtype=1",
    "0", "1", "2", "Stream3", "video", "channel1", "main"
]

print(f"[*] {ip}:{port} पर RTSP पाथ्स की टेस्टिंग शुरू हो रही है...\n")

for path in paths:
    url = f"rtsp://{ip}:{port}/{path}"
    # ffprobe को बैकग्राउंड में चलाकर केवल रिस्पॉन्स चेक करना
    cmd = ["ffprobe", "-v", "error", "-rtsp_transport", "tcp", "-timeout", "3000000", url]
    
    try:
        # कमांड रन करें और उसका एरर आउटपुट कैप्चर करें
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stderr
        
        if "404" in output:
            print(f"[-] /{path} -> Not Found (404)")
        elif "401" in output or "Unauthorized" in output:
            print(f"[+] [FOUND AUTH] /{path} -> पासवर्ड प्रोटेक्टेड है (401 Unauthorized)!")
            break
        else:
            # अगर कोई एरर नहीं आया या कुछ और आया
            if result.returncode == 0:
                print(f"[==>] [SUCCESS] /{path} -> स्ट्रीम पूरी तरह खुली है!")
                break
            else:
                print(f"[-] /{path} -> {output.strip()}")
    except Exception as e:
        print(f"[-] त्रुटि /{path}: {str(e)}")

print("\n[*] स्कैनिंग पूरी हुई।")
