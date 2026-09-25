import re
import urllib.parse
import requests
from django.conf import settings

def clean_phone_number(phone_str):
    """
    Cleans and standardizes the phone number (E.164 format without +).
    Defaults to India country code (91) if 10 digits are provided.
    """
    if not phone_str:
        return None
    cleaned = re.sub(r'[^0-9]', '', str(phone_str))
    if len(cleaned) == 10:
        cleaned = '91' + cleaned
    elif len(cleaned) == 12 and cleaned.startswith('91'):
        pass
    return cleaned

def send_whatsapp_alert(name, phone, date_time_str):
    """
    Automated WhatsApp alert containing Name, Number, and Time.
    Supports CallMeBot gateway and Meta WhatsApp API.
    """
    msg_text = (
        f"✨ *New Appointment Booking - Sukhmani Designer* ✨\n\n"
        f"👤 *Name:* {name}\n"
        f"📞 *Number:* {phone}\n"
        f"⏰ *Time:* {date_time_str}\n\n"
        f"📍 Sukhmani Designer"
    )

    designer_phone = getattr(settings, 'WHATSAPP_DESIGNER_PHONE', '918284099286')
    callmebot_key = getattr(settings, 'CALLMEBOT_API_KEY', None)

    # 1. Try CallMeBot Automated Gateway
    if callmebot_key:
        try:
            target_phone = '+' + clean_phone_number(designer_phone)
            encoded_msg = urllib.parse.quote_plus(msg_text)
            url = f"https://api.callmebot.com/whatsapp.php?phone={target_phone}&text={encoded_msg}&apikey={callmebot_key}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                print(f"[WhatsApp CallMeBot] Alert sent to {target_phone} successfully!")
                return True
            else:
                print(f"[WhatsApp CallMeBot] Error response ({resp.status_code}): {resp.text}")
        except Exception as e:
            print(f"[WhatsApp CallMeBot] Exception: {repr(e)}")

    # 2. Try Meta WhatsApp Cloud API
    meta_token = getattr(settings, 'WHATSAPP_API_TOKEN', None)
    meta_phone_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None)
    if meta_token and meta_phone_id:
        try:
            recipient = clean_phone_number(designer_phone)
            url = f"https://graph.facebook.com/v20.0/{meta_phone_id}/messages"
            headers = {
                "Authorization": f"Bearer {meta_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"body": msg_text}
            }
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code in [200, 201]:
                print(f"[WhatsApp Meta API] Sent successfully to {recipient}")
                return True
        except Exception as e:
            print(f"[WhatsApp Meta API] Error: {repr(e)}")

    return False

send_whatsapp_message = send_whatsapp_alert
