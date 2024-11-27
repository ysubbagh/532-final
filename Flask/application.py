from flask import Flask, render_template, jsonify
import requests
import os

MAX_LEVEL = 89  # Distance when the tank is empty (in cm)

application = Flask(__name__, template_folder='templates')

# URL to my AWS API Gateway endpoint
API_URL = "https://w8wla8op08.execute-api.us-east-1.amazonaws.com/prod/data?device_id="

# tank numbers to their device IDs
TANK_DEVICE_IDS = {
    "tank1": 1,
    "tank2": 2,
    "tank3": 3
}

# get the water level of a tank via the API given its device_id
def fetch_water_levels():
    water_levels = {}
    for tank, device_id in TANK_DEVICE_IDS.items():
        try:
            # Construct the API URL for the tank
            url = f"{API_URL}{device_id}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract distance from the response
            if isinstance(data, list) and len(data) > 0:
                payload = data[0].get("payload", {})
                distance = payload.get("distance", None)  # Return None if distance is not found
            else:
                distance = None
            
            # Add the tank's level to the dictionary
            water_levels[tank] = distance if distance is not None else 0  # Default to 0 if unavailable
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {tank}: {e}")
            water_levels[tank] = 0  # Default to 0 in case of an error
    return water_levels

@application.route("/")
def index():
    # get distance
    water_levels = fetch_water_levels()

    # Compute percentage and status for each tank
    tank_status = {}
    for tank, level in water_levels.items():
        percentage = MAX_LEVEL - (level / MAX_LEVEL) * 100
        if percentage >= 80:
            status = "high"  # Green thumbs-up
        elif percentage <= 20:
            status = "low"  # Red thumbs-down
        else:
            status = "normal"  # No icon
        tank_status[tank] = {"level": level, "percentage": percentage, "status": status}

    #debug 
    print("Fetched Water Levels:", water_levels)
    print("Templates Directory:", application.template_folder)
    print("Absolute Path to Templates Directory:", os.path.abspath(application.template_folder))

    water_percentages = {tank: (level / MAX_LEVEL) * 100 for tank, level in water_levels.items()}
    return render_template('index.html', tank_status=tank_status)

if __name__ == "__main__":
    application.run(debug=True)
