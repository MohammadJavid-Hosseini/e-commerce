from config.celery import app
from django.core.mail import send_mail
from decouple import config


@app.task
def send_order_confirmation_email(customer_email, order_id):
    subject = f"Confirmation email {order_id}"
    message = f"Your order: {order_id} is confirmed!"
    from_email = config('BUSINESS_EMAIL')

    print(f"Sending email to {customer_email} from {from_email}")
    print(f"Subject: {subject}")
    print(f"Message: {message}")
    send_mail(subject, message, from_email, [customer_email])
