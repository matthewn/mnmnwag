from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.template.response import TemplateResponse

from .models import Subscription
from .utils import send_confirmation_email


def sub_create(request):
    context = {'page_message': 'oooh! a new subscriber!'}
    if request.method == 'POST':
        try:
            sub = Subscription.objects.create(email=request.POST['email'])
        except IntegrityError:
            sub = Subscription.objects.get(email=request.POST['email'])
        send_confirmation_email(request, sub)
        send_mail(f'mnmnwag: sub requested by {sub.email} [eom]', '', None, [settings.ADMINS[0][1]])
        context['email'] = sub.email
    return TemplateResponse(request, 'subs/create.html', context)


def sub_confirm(request, uuid):
    sub = Subscription.objects.get(id=uuid)
    sub.is_active = True
    sub.save()
    send_mail(f'mnmnwag: sub confirmed for {sub.email} [eom]', '', None, [settings.ADMINS[0][1]])
    return TemplateResponse(
        request,
        'subs/message.html',
        {
            'email': sub.email,
            'message': f'Subscription confirmed for: {sub.email}',
            'page_message': 'oooh! a new subscriber!',
        }
    )


def sub_remove(request, uuid):
    sub = Subscription.objects.get(id=uuid)
    sub.is_active = False
    sub.save()
    return TemplateResponse(
        request,
        'subs/message.html',
        {
            'email': sub.email,
            'message': f'Subscription removed for: {sub.email}',
            'page_message': 'oh no! sorry to see you go.',
        }
    )
