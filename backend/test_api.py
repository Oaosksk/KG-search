import requests
import json

# Get a token first (you'll need to replace with actual token)
url = "http://localhost:8000/search/"

# You need to get the actual JWT token from your browser
# For now, let's just check if the endpoint is responding
response = requests.post(
    url,
    json={"query": "How many customers do we have?", "top_k": 5},
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")
