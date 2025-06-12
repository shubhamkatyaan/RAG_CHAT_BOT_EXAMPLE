import os, requests
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"
headers = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}
resp = requests.post(API_URL, headers=headers, json={"inputs":"Test"})
print(resp.status_code, resp.json())
