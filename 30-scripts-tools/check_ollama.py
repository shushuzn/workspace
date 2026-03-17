import requests
resp = requests.get("http://localhost:11434/api/tags", timeout=5)
if resp.status_code == 200:
    tags = resp.json()
    for m in tags['models']:
        if 'qwen' in m['name'].lower():
            print(f"{m['name']}: {m['details']['parameter_size']} ({m['details']['quantization_level']})")
else:
    print(f"Error: {resp.status_code}")
