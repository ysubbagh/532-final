import smtplib
import requests

#constants for distances in the water drum
FULL = 0
EMPTY = 35
WARNING_ADJUST = 5

#email details
to_email = "ysubbagh@gmail.com"  # recipient's email
from_email = "ydns10@gmail.com"  # sender's email
password = "yasminesubbagh"  # sender email password

# fetch distance from AWS REST API given the device_id
def fetch_distance(device_id):
    api_url = 'https://w8wla8op08.execute-api.us-east-1.amazonaws.com/prod/data?device_id=${device_id}'
    response = requests.get(api_url)
    data = response.json()
    return data['distance'] 

# send email
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

#main, check distance and send email if needed
def main():
    device_id = 0
    distance = fetch_distance(device_id)
    levelPerc = (FULL - distance) / FULL * 100
    
    if distance <= FULL + WARNING_ADJUST: # Tank is almost full( 5in from top) , send an email
        body = f"The water tank is almost full. Current distance: {distance} aka {levelPerc}%."
        send_email(body)
    elif distance >= EMPTY - WARNING_ADJUST: # tank is almost empty ( 5in from bottom ), send an email
        body = f"The water tank is almost empty. Current distance: {distance} aka {levelPerc}%."
        send_email(body)

if __name__ == "__main__":
    main()