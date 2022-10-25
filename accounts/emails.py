from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from accounts.models import UserAuthToken


def send_login_code(user):
    # use email css framework like:
    # https://get.foundation/emails.html
    subject = _("Login Code for Datenwerft")
    try:
        code = user.userauthtoken.email_token
    except UserAuthToken.DoesNotExist:
        email_body = {
            'content': _("Something wrong, place restart login process"),
            'code': None,
            'user': user
        }
    else:
        email_body = {
            'content': _("Please enter this code to authenticate"),
            'code': code,
            'user': user
        }
    template = 'accounts/email'
    html_template = render_to_string(f'{template}.html', email_body)
    txt_template = render_to_string(f'{template}.txt', email_body)
    message = EmailMultiAlternatives(
        subject=subject,
        body=txt_template,
        to=[user.email])
    message.attach_alternative(html_template, "text/html")
    return message.send()
