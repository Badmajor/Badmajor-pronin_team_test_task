from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

TEMPLATES = {
    "Collect": "create_collect.html",
    "Payment": "create_payment.html",
}


def get_email(obj) -> str:
    if hasattr(obj, "author"):
        return obj.author.email
    return obj.donator.email


@shared_task
def task_send_email(obj):
    template = TEMPLATES.get(obj.__class__.__name__)
    email = get_email(obj)
    html_message = render_to_string(template, {"obj": obj})
    message = strip_tags(html_message)
    send_mail(
        f"Ваш {obj.__class__.__name__} создан",
        message,
        "info@proninteam",
        (email,),
        html_message,
    )
