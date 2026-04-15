from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from .models import Subscription
from .utils import send_confirmation_email


def sub_create(request):
    if 'mahnamahna' not in request.get_host():
        raise Http404
    context = {'page_message': 'oooh! a new subscriber!'}
    if request.method == 'POST':
        # check our homegrown checkbox captcha fields
        # (silent fail if they get it wrong is deliberate)
        nope = request.POST.get('nope')
        yep = request.POST.get('yep')
        if nope is None and yep == 'on':
            email = request.POST.get('email', '')
            try:
                validate_email(email)
            except ValidationError:
                context['error'] = 'Please enter a valid email address.'
            else:
                sub, created = Subscription.objects.get_or_create(email=email)
                if created or not sub.is_active:
                    send_confirmation_email(request, sub)
                    send_mail(f'mnmnwag: sub requested by {sub.email} [eom]', '', None, [settings.ADMINS[0][1]])
                else:
                    context['already_active'] = True
                context['email'] = sub.email
    return TemplateResponse(request, 'subs/create.html', context)


def sub_confirm(request, uuid):
    if 'mahnamahna' not in request.get_host():
        raise Http404
    sub = get_object_or_404(Subscription, id=uuid)
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
    if 'mahnamahna' not in request.get_host():
        raise Http404
    sub = get_object_or_404(Subscription, id=uuid)
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
