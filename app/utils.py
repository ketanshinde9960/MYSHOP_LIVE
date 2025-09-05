from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.template.loader import render_to_string

def send_email_verification_OTP(client_email, code):
    try: 
        subject = 'OTP Confirmation - EliteElectronics.com'
        template = 'verification_email.html'
        context = {
            'code': code
            # Add more context variables as needed
        }

        message = render_to_string(template, context)
        from_email = settings.EMAIL_HOST_USER

        send_mail(subject, message, from_email, [client_email], html_message=message, fail_silently=False)

        # If the email is sent successfully, return True
        return True

    except Exception as e:
        # If an error occurs, return False
        print(f"An error occurred while sending email: {str(e)}")
        return False
    


def send_order_confirmation_email(client_email, order_id, order_date, client_name):
    try:
        subject = 'Order Confirmation - EliteElectronics.com'
        template = 'order_confirmation_email.html'

        context = {
            'client_name': client_name,
            'order_id': order_id,
            'order_date': order_date,
            # Add more context variables as needed
        }

        message = render_to_string(template, context)
        from_email = settings.EMAIL_HOST_USER

        send_mail(subject, message, from_email, [client_email], html_message=message, fail_silently=False)

        # If the email is sent successfully, return True
        return True

    except Exception as e:
        # If an error occurs, return False
        print(f"An error occurred while sending order confirmation email: {str(e)}")
        return False

