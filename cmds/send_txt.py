import requests

class SMSNotifier:
    """Class to send SMS notifications via Sendinblue API."""
    
    def __init__(self, api_key, sender, recipient):
        """Initialize with API key, sender name, and recipient phone number."""
        self.api_key = api_key
        self.sender = sender
        self.recipient = recipient
        self.url = "https://api.sendinblue.com/v3/transactionalSMS/sms"
        self.headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def send_sms(self, message):
        """Send an SMS message via the Sendinblue API."""
        data = {
            "sender": self.sender,
            "recipient": self.recipient,
            "content": message
        }
        
        try:
            response = requests.post(self.url, json=data, headers=self.headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            
            # Check if response is successful
            if response.status_code == 201:
                print("✅ SMS sent successfully!")
            else:
                print(f"❌ Failed to send SMS: {response.text}")
                
        except requests.exceptions.HTTPError as http_err:
            print(f"❌ HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"❌ Request error occurred: {req_err}")
    
def main():
    """Main function to send an SMS notification."""
    api_key = 'your_sendinblue_api_key'
    sender = 'your_sender_name'
    recipient = 'your_phone_number'

    notifier = SMSNotifier(api_key, sender, recipient)
    message = 'Your temperature is too high!'  # Example message
    notifier.send_sms(message)

if __name__ == "__main__":
    main()
