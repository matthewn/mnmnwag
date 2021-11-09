from django.core.mail import send_mail
from django.template.loader import get_template

from urllib.parse import urlparse

from .models import Subscription


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
    send_mail(f'please confirm your subscription for {host}', body, None, (subscription.email,))


def send_notifications(posts):
    template = get_template('subs/notification_email.txt')
    subs = Subscription.objects.filter(is_active=True)
    host = urlparse(posts.first().full_url).netloc
    if posts.count() > 1:
        subject = 'new posts on mahnamahna.net'
    else:
        subject = 'new post on mahnamahna.net'
    for sub in subs:
        context = {
            'posts': posts,
            'uuid': sub.id,
            'host': host,
        }
        body = template.render(context)
        send_mail(subject, body, None, (sub.email,))
