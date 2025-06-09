import requests

API_URL = "https://api-inference.huggingface.co/models/nlptown/bert-base-multilingual-uncased-sentiment"
API_TOKEN = "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"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

def analyze_sentiment(comment_text):
    try:
        response = requests.post(API_URL, headers=HEADERS, json={"inputs": comment_text})
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            return "neutral"
            
        result = response.json()
        print("API Response:", result)

        # Get the label from the first result
        label = result[0][0]["label"].lower()
        
        # Convert label to numeric value
        rating = int(label.split()[0])
        
        # Classify based on 5-star rating
        if rating <= 2:
            return "negative"
        elif rating == 3:
            return "neutral"
        elif rating >= 4:
            return "positive"
        else:
            return "neutral"
            
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return "neutral"