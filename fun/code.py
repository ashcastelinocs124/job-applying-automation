import requests




open_router_api_key = "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"
API_URL = 'https://openrouter.ai/api/v1/chat/completions'

headers = {
    'Authorization': f'Bearer {open_router_api_key}',
    'Content-Type': 'application/json'
}


data = {
    "model": "deepseek/deepseek-chat",
    "messages": [{"role": "user", "content": "What's the best way to learn programming?"}]
}

# Send the request
response = requests.post(API_URL, json=data, headers= headers)

# Check if it worked
if response.status_code == 200:
    # Extract and print just the AI's response text
    ai_message = response.json()['choices'][0]['message']['content']
    print(f"DeepSeek says: {ai_message}")
else:
    print(f"Oops! Something went wrong. Status code: {response.status_code}")
    print(f"Error details: {response.text}")