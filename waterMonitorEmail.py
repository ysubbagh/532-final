import smtplib
import requests

# Constants for distances in the water drum
FULL = 0         # Distance when the tank is full 
EMPTY = 89       # Distance when the tank is empty (in cm)
WARNING_ADJUST = 10 # lil more than 10%  

# Email creds
to_email = "ysubbagh@gmail.com"  
from_email = "ydns10@gmail.com"  
password = "yasminesubbagh"     

# AWS REST API URL 
API_URL = "https://w8wla8op08.execute-api.us-east-1.amazonaws.com/prod/data?device_id={device_id}"

# Tank IDs to monitor
TANKS = [1, 2, 3]  

# Fetch distance from AWS REST API given the device_id
def fetch_distance(device_id):
    try:
        response = requests.get(API_URL.format(device_id=device_id))
        response.raise_for_status()
        data = response.json()
        payload = data[0].get("payload", {})
        distance = payload.get("distance", None) 
        return distance  
    except Exception as e:
        print(f"Error fetching distance for device_id {device_id}: {e}")
        return None

# Send email
def send_email(body):
    subject = "Water Tank Alert"
    message = f"Subject: {subject}\n\n{body}"
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, password)
            server.sendmail(from_email, to_email, message)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

# check distances for all tanks and send alerts if needed
def main():
    for tank_id in TANKS:
        distance = fetch_distance(tank_id)
        if distance is None:
            print(f"Skipping tank {tank_id} due to fetch error.")
            continue
        
        levelPerc = ((EMPTY - distance) / (EMPTY - FULL)) * 100  # Calculate level percentage
        
        # Check if the tank is almost full or empty
        if distance <= FULL + WARNING_ADJUST:  # Almost full
            body = f"Tank {tank_id} is almost full. Current distance: {distance} centimeters ({levelPerc:.2f}%)."
            print(body)
            send_email(body)
        elif distance >= EMPTY - WARNING_ADJUST:  # Almost empty
            body = f"Tank {tank_id} is almost empty. Current distance: {distance} cectimeters ({levelPerc:.2f}%)."
            print(body)
            send_email(body)
        else: # no email if safe levels
            print(f"Tank {tank_id} is at a safe level: {distance} inches ({levelPerc:.2f}%).")

if __name__ == "__main__":
    main()
