from django.db import IntegrityError
from django.template.response import TemplateResponse

from .models import Subscription
from .utils import send_confirmation_email


def sub_create(request):
    if request.method == 'POST':
        try:
            sub = Subscription.objects.create(email=request.POST['email'])
        except IntegrityError:
            sub = Subscription.objects.get(email=request.POST['email'])

        send_confirmation_email(request, sub)

        return TemplateResponse(
            request,
            'subs/create.html',
            {
                'email': sub.email,
                'page_message': 'oooh! a new subscriber!',
            }
        )
    return TemplateResponse(request, 'subs/create.html', {})


def sub_confirm(request, uuid):
    sub = Subscription.objects.get(id=uuid)
    sub.is_active = True
    sub.save()
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
