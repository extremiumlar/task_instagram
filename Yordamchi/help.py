import threading
import re
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError

email_regax = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

class EmailThread(threading.Thread):
    def __init__(self, email):
        threading.Thread.__init__(self)
        self.email = email
    def run(self):
        self.email.send()

class Email :
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to = data['to_email'],
        )
        if data.get('content_type')=='html':
            email.content_subtype = 'html'
        EmailThread(email).start()
def send_email(email, kod):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {'kod': kod},
    )
    Email.send_email(
        {
            'subject': "Ro'yxatdan o'tish",
            'to_email': [email],
            'body': html_content,
            'html_content': "html",
        }
    )

def check_email_or_phone(email_or_phone):
    # phone_number = phonenumbers.parse(email_or_phone)
    if re.fullmatch(email_regax, email_or_phone):
        email_or_phone = "email"
    else:
        data = {
            "success": False,
            "message": "Email yoki telefon raqam xato kiritildi .",
        }
        raise ValidationError(data)

    return email_or_phone
