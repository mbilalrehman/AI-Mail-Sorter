Zenbox AI - Intelligent Email Sorter

A hybrid Python (Flask) and JavaScript web application that uses AI to scan and categorize your Gmail inbox in real-time.

This project uses a secure hybrid model:

Frontend (HTML/JS): Handles Google OAuth 2.0 login to get a secure access token from the user.

Backend (Python/Flask): Receives the access token from the frontend, builds the Gmail service, performs the AI analysis (using VADER), and sends the sorted data back as JSON.

Tech Stack

Backend: Python, Flask, Flask-CORS

Frontend: HTML, TailwindCSS, JavaScript (Fetch API)

AI / NLP: VADER (Sentiment Analysis)

API: Google Gmail API (OAuth 2.0)

AI Sorting Logic (v4)

The core of this project is the analyze_email function, which uses a priority-based "hybrid" approach to categorize emails accurately:

Priority 1: High-Confidence Spam (e.g., "unsubscribe" links)

Priority 2: High-Confidence Security (e.g., regex for "login from", "password reset")

Priority 3: High-Confidence Invoices (e.g., "invoice", "payment due")

Priority 4: High-Confidence Finance Updates (e.g., "receipt", "payment received")

Priority 5: Urgent Sentiment (VADER) (e.g., angry client emails)

Priority 6 & 7: Low-priority updates and general promotions.

How to Run This Project Locally

Prerequisites:

Python 3

Google Cloud Project with "Web application" credentials.

1. Google Cloud Setup:

Create a "Web application" OAuth 2.0 Client ID.

Add http://localhost:8000 to the "Authorized JavaScript origins" and Save.

Copy this CLIENT_ID.

2. Frontend (index.html):

Paste your CLIENT_ID into the index.html file (line 143).

3. Run the Backend (Terminal 1):

# Install libraries
pip install Flask flask-cors google-api-python-client google-auth vaderSentiment

# Run the Flask server
python app.py
# Server will run on http://localhost:5000


4. Run the Frontend (Terminal 2):

# In a new terminal, run the simple web server
python -m http.server 8000
# Server will run on http://localhost:8000


5. Run the App:

Open your browser and go to http://localhost:8000/index.html

Click "Connect Your Gmail Account" and log in via the pop-up.

Click "Scan My 25 Most Recent Emails" to get the AI report.
