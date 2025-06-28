from ....core.config import config
from ....core import http
from pprint import pprint

async def send_message(phone_number: str, message: str):
    url = f"{config.graph_facebook_url}/{config.whatsapp_phone_id}/messages"
    print("================================================")
    print("Sending message")
    print(f"To {phone_number}")
    print(f"Message: {message}")
    print(f"POST {url}")
    print("================================================")
    headers = {
        "Authorization": f"Bearer {config.whatsapp_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "text",
        "text": {"body": message},
    }
    response = await http.post(url, headers=headers, data=data)
    pprint(response)
    print("================================================")
    return response