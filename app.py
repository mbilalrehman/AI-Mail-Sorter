import base64
import email
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from flask import Flask, jsonify, request # 'request' ko import karein
from flask_cors import CORS
from google.oauth2.credentials import Credentials # Sirf 'Credentials' import karein
import re

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app) 

# --- AI Setup (Same as before) ---
analyzer = SentimentIntensityAnalyzer()

# (SpaCy ki zaroorat nahi kyun k V3 logic use kar rahay hain)

def analyze_email(body):
    """
    Aapka AI logic (Version 4 - Hybrid & 100% Strong)
    Yeh function priority k hisab se chalta hai.
    """
    body_lower = body.lower()
    
    # --- Priority 1: High-Confidence Spam (Unsubscribe) ---
    # Agar email mein "unsubscribe" hai, toh yeh 99.9% promotion hai.
    # Isay pehlay hi pakar lein taakay yeh doosri categories mein na ghalat-fehmi na karay.
    if "unsubscribe" in body_lower or "view this email in your browser" in body_lower:
        return "SPAM/PROMOTION"

    # --- Priority 2: High-Confidence Security (Specific Phrases) ---
    # Hum specific phrases k liye Regex use karein gay taakay ghalti na ho.
    # "personalize your security" isay ignore karega, lekin "security alert" ko pakar lega.
    if re.search(r"(security alert|login from|unrecognized device|password (changed|reset)|suspicious activity|was disconnected)", body_lower):
        return "SECURITY ALERT"

    # --- Priority 3: High-Confidence Invoices (Money DUE) ---
    # Yeh check karega k "invoice" ya "overdue" k lafz mojood hain,
    # lekin "receipt" ya "paid" k lafz mojood NAHI hain.
    if ("invoice" in body_lower or "payment due" in body_lower or "overdue" in body_lower) and not ("receipt" in body_lower or "paid" in body_lower or "received your payment" in body_lower):
        return "INVOICE/BILL"

    # --- Priority 4: High-Confidence Finance Updates (Money Confirmed) ---
    if "receipt" in body_lower or "payment received" in body_lower or "we received your payment" in body_lower:
        return "FINANCE UPDATE"

    # --- Priority 5: Urgent Sentiment (VADER) ---
    # Agar oopar wala kuch nahi hai, TOH ab sentiment check karein.
    # Is tarah ek "angry" spam email "URGENT" nahi banay ga.
    sentiment_score = analyzer.polarity_scores(body)['compound']
    if sentiment_score < -0.3:
        return "URGENT_CLIENT"

    # --- Priority 6: Low-Priority Account Updates ---
    if "confirm your email" in body_lower or "personalize your security" in body_lower or "billing method" in body_lower or "added a card" in body_lower:
        return "ACCOUNT UPDATE"

    # --- Priority 7: General Promotions (Catch-all) ---
    if "newsletter" in body_lower or "recommendation" in body_lower or "congrats" in body_lower or "% off" in body_lower or "limited time offer" in body_lower:
        return "SPAM/PROMOTION"

    # --- Default ---
    return "OTHER"

def fetch_and_sort_emails(service): # Ab 'service' ko argument k taur par lein
    """
    Yeh function 'print' k bajaye 'return' karega.
    """
    if not service:
        return {"error": "Could not connect to Gmail service."}

    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=25).execute()
    messages = results.get('messages', [])
    
    email_results = []
    categories_summary = {}

    if not messages:
        return {"emails": [], "summary": {}}
    else:
        # (Email fetching logic bilkul same hai)
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            subject = "No Subject"
            sender = "Unknown Sender"
            headers = msg['payload']['headers']
            for header in headers:
                if header['name'] == 'Subject': subject = header['value']
                if header['name'] == 'From': sender = header['value'].split('<')[0]
                    
            body = ""
            if 'parts' in msg['payload']:
                parts = msg['payload']['parts']
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        body = base64.urlsafe_b64decode(data.replace('-', '+').replace('_', '/')).decode('utf-8')
                        break
            elif 'body' in msg['payload']:
                data = msg['payload']['body']['data']
                body = base64.urlsafe_b64decode(data.replace('-', '+').replace('_', '/')).decode('utf-8')
            
            if body:
                category = analyze_email(body)
                email_results.append({"subject": subject, "sender": sender, "category": category})
                categories_summary[category] = categories_summary.get(category, 0) + 1
            
    return {"emails": email_results, "summary": categories_summary}

# --- Naya Flask API Endpoint ---
@app.route('/scan-emails', methods=['POST']) # Ab yeh POST request hai
def scan_emails_api():
    """
    Yeh API frontend se Access Token le ga.
    """
    print("Request received... Trying to get access token.")
    
    # Step 1: Frontend se Access Token haasil karein
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Authorization header missing."}), 401
        
    try:
        # "Bearer <token>" se token nikaalein
        access_token = auth_header.split(' ')[1]
        
        # Step 2: Uss token se 'credentials' banayein
        creds = Credentials(token=access_token)
        
        # Step 3: Uss token se Gmail 'service' banayein
        service = build('gmail', 'v1', credentials=creds)
        print("Gmail service built successfully using user's token.")
        
        # Step 4: Puraana function call karein
        data = fetch_and_sort_emails(service)
        print("Scan complete. Sending data back to website.")
        
        return jsonify(data)
        
    except HttpError as error:
        print(f"An error occurred: {error}")
        return jsonify({"error": f"Gmail API Error: {error}"}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500


if __name__ == '__main__':
    print("Starting Zenbox AI Flask Server at http://localhost:5000")
    # Ab 'credentials.json' ki zaroorat nahi
    app.run(port=5000, debug=False) # Debug mode off kar dein

