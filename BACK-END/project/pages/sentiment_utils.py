import requests

API_URL = "https://api-inference.huggingface.co/models/nlptown/bert-base-multilingual-uncased-sentiment"
API_TOKEN = "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"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

def analyze_sentiment(comment_text):
    response = requests.post(API_URL, headers=HEADERS, json={"inputs": comment_text})
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return "neutral"
    result = response.json()
    print("API Response:", result)

    label = result[0][0]["label"].lower()

    if "1" in label or "2" in label:
        return "negative"
    elif "3" in label:
        return "neutral"
    elif "4" in label or "5" in label:
        return "positive"
    else:
        return "neutral"