# filters.py
from django import template

register = template.Library()


@register.filter(name="hide_email")
def hide_email(email):
    if email:
        parts = email.split('@')
        username = parts[0]
        domain = parts[1]
        hidden_username = f"{username[:3]}{'*' * (len(username) - 3)}"
        return f"{hidden_username}@{domain}"
    return ""


@register.filter(name="hide_phone")
def hide_phone(phone_number):
    if phone_number:
        hidden_phone = f"{'*' * (len(phone_number) - 4)}{phone_number[-4:]}"
        return hidden_phone
    return ""
