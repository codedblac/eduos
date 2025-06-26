import africastalking
from django.conf import settings

# Initialize Africa's Talking
africastalking.initialize(
    username=settings.AT_USERNAME,  # sandbox or production
    api_key=settings.AT_API_KEY
)

sms = africastalking.SMS

def send_sms(phone_number, message):
    """
    Sends SMS using Africa's Talking.
    Ensure phone_number is in international format (e.g. +2547xxxxxxx)
    """
    try:
        # Format phone number
        if phone_number.startswith('0'):
            phone_number = '+254' + phone_number[1:]
        elif not phone_number.startswith('+'):
            phone_number = '+254' + phone_number

        response = sms.send(message, [phone_number])
        return response
    except Exception as e:
        print(f"SMS sending failed: {e}")
        return None


def send_notification_to_user(user, title, message):
    """
    Sends an in-app or system notification to a specific user.
    You can later expand this to include email, push, SMS, etc.
    """
    from notifications.models import Notification  # adjust path if needed

    Notification.objects.create(
        recipient=user,
        title=title,
        message=message
    )
    
    
def notify_user(user, title, message, via_sms=False):
    send_notification_to_user(user, title, message)
    
    if via_sms and hasattr(user, 'phone_number'):
        send_sms(user.phone_number, f"{title}: {message}")    