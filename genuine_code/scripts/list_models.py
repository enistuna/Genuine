import os, requests, json
from dotenv import load_dotenv

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'))

api_key = os.getenv("GEMINI_API_KEY")
print(f"Using API Key: {api_key[:5]}... (Length: {len(api_key)})")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        models = response.json().get('models', [])
        print("\nAvailable Models for generateContent:")
        for m in models:
            if "generateContent" in m.get("supportedGenerationMethods", []):
                print(f"- {m['name']} ({m['displayName']})")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Exception: {e}")
