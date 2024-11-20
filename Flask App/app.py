from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# API URL to fetch water tank data (change this to your actual API URL)
API_URL = "https://your-api-gateway-url/dev/get-data?device_id=0"

@app.route('/')
def index():
    # Fetch data from the API
    try:
        response = requests.get(API_URL)
        data = response.json()
    except requests.exceptions.RequestException as e:
        data = {'error': str(e)}
    
    # Render the HTML template and pass data to it
    return render_template('index.html', data=data)

if __name__ == "__main__":
    # Run the Flask app on the server's IP and make it accessible on port 80
    app.run(host="0.0.0.0", port=80)
