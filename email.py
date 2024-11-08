import smtplib
import requests

# Function to fetch distance from REST API
def fetch_distance(api_url):
    response = requests.get(api_url)
    data = response.json()
    return data['distance'] 

# Function to send email
def send_email(subject, body, to_email, from_email, password):
    message = f"Subject: {subject}\n\n{body}"
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, password)
            server.sendmail(from_email, to_email, message)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Main function
def main():
    api_url = 'http://example.com/api/distance'  # Replace with your API URL
    distance = fetch_distance(api_url)
    
    if distance > 8:
        subject = "Water Tank Alert"
        body = f"The distance is over 8. Current distance: {distance}"
        to_email = "ysubbagh@gmail.com"  # Replace with recipient's email
        from_email = "ydns10@gmail.com"  # Replace with your email
        password = "yasminesubbagh"  # Replace with your email password
        
        send_email(subject, body, to_email, from_email, password)

if __name__ == "__main__":
    main()