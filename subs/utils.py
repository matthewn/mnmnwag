from django.core.mail import send_mail
from django.template.loader import get_template


def send_confirmation_email(request, subscription):
    template = get_template('subs/confirm_email.txt')
    host = request.get_host()
    context = {
        'email': subscription.email,
        'uuid': subscription.id,
        'host': host,
        'protocol': request.META['wsgi.url_scheme'],
    }
    body = template.render(context)
    send_mail(f'subscription confirmation from {host}', body, None, (subscription.email,))
