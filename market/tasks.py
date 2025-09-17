from config.celery import app
from django.core.mail import send_mail
from decouple import config


@app.task
def send_order_creation_email(customer_email, order_id):
    subject = "Order recieved"
    message = f"Thanks for your purchase; your order {order_id} is recieved"
    from_email = config('EMAIL_HOST_USER')

    send_mail(subject, message, from_email, [customer_email])


@app.task
def send_order_confirmation_email(customer_email, order_id):
    subject = f"Confirmation email {order_id}"
    message = f"Your order: {order_id} is confirmed; It's ready for the payment"
    from_email = config('EMAIL_HOST_USER')

    send_mail(subject, message, from_email, [customer_email])
