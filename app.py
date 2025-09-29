from flask import Flask, render_template
import threading
import time
import requests
import os

app = Flask(__name__)

# Function to ping the app itself
def ping_self():
    while True:
        try:
            # Get the Render URL (works in production) or localhost (for development)
            url = os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:8080')
            print(f"Pinging: {url}")
            response = requests.get(url)
            print(f"Ping successful: {response.status_code}")
        except Exception as e:
            print(f"Ping failed: {e}")
        
        # Ping every 10 minutes (600 seconds)
        time.sleep(600)

@app.route('/')
def hello():
    return "Hello World"

# Health check endpoint for the pinger
@app.route('/health')
def health():
    return "OK", 200

# Start the pinger thread when the app starts
if not os.getenv('RENDER'):
    # Development environment - don't start pinger automatically
    pass
else:
    # Production environment - start the pinger
    ping_thread = threading.Thread(target=ping_self)
    ping_thread.daemon = True
    ping_thread.start()

#if __name__ == '__main__':
app.run(host='0.0.0.0', port=8080)
