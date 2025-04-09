import requests

def send_sms(message):
    url = "https://api.sendinblue.com/v3/transactionalSMS/sms"
    headers = {
        'api-key': 'your_sendinblue_api_key',
        'Content-Type': 'application/json'
    }
    data = {
        "sender": "your_sender_name",
        "recipient": "your_phone_number",
        "content": message
    }
    response = requests.post(url, json=data, headers=headers)
    print(response.json())

# Example usage
send_sms('Your temperature is too high!')
