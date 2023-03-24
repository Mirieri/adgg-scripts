import requests
import json
import os

WA_PHONE_NUMBER = '14155238886'
WA_BASE_URL = f"https://graph.facebook.com/v16.0/me/messages?access_token={os.getenv('WHATSAPP_ACCESS_TOKEN')}"

headers = {
    'Content-type': 'application/json'
}
    
def send_message(phone_number, message):
    payload = {
        'recipient': {'phone_number': phone_number},
        'message': {"text": message},
        'messaging_type': 'RESPONSE',
        'sender': {'phone_number': WA_PHONE_NUMBER}
    }
    response = requests.post(url=WA_BASE_URL, headers=headers, data=json.dumps(payload))
    print(response.json())

def process_message(message):
    phone_number = message['from']
    text = message['text']
    
    if "amount of milk collected" in text.lower():
        send_message(phone_number, "Thank you")
    
    # Handle other incoming messages here
    
while True:
    response = requests.get(f'https://api.zuri.chat/message/read/{os.getenv("GROUP_CHAT_ID")}')
    
    try:
        messages = response.json()['data']['messages']
        for message in messages:
            process_message(message['content'])
    except KeyError:
        print('No new messages')
