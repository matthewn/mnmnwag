import logging

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from mnmnwag.utils import get_client_ip

from .forms import SubscriptionForm
from .models import Subscription
from .utils import send_confirmation_email

logger = logging.getLogger(__name__)

# Rate limits for subscription signups. Generous enough that no real visitor
# will ever see them; tight enough that a bot can't use us as a mail cannon.
SUB_RATE_LIMIT_IP = 5  # max signup attempts per IP per hour
SUB_RATE_LIMIT_IP_PERIOD = 3600
SUB_RATE_LIMIT_EMAIL = 3  # max signup attempts per email address per day
SUB_RATE_LIMIT_EMAIL_PERIOD = 86400

# Site-wide cap on signups per period, so the form can't be used as a mail
# cannon by an attacker with enough IPs to walk around the per-client limits.
SUB_GLOBAL_LIMIT = 20
SUB_GLOBAL_PERIOD = 3600

RATE_LIMIT_MESSAGE = 'Too many subscription attempts. Please try again later.'


def is_rate_limited(key, limit, period):
    """
    Increment the counter at `key` and report whether it has passed `limit`.
    """
    cache.add(key, 0, period)
    try:
        count = cache.incr(key)
    except ValueError:
        # The key expired between the add() and the incr(); treat as first hit.
        return False
    return count > limit


def alert_admin_once():
    """
    Email the admin that the global limit tripped, at most once per period.
    """
    if cache.add('sub_breaker_alerted', True, SUB_GLOBAL_PERIOD):
        send_mail('mnmnwag: subscription send limit reached [eom]', '', None, [settings.ADMINS[0][1]])


def sub_create(request):
    if 'mahnamahna' not in request.get_host():
        raise Http404

    context = {'page_message': 'oooh! a new subscriber!'}

    def respond(status=200):
        return TemplateResponse(request, 'subs/create.html', context, status=status)

    if request.method != 'POST':
        context['form'] = SubscriptionForm()
        return respond()

    form = context['form'] = SubscriptionForm(request.POST)
    ip = get_client_ip(request)

    # Checked before validation, so that a bot tripping the traps over and
    # over still runs itself out of attempts.
    if is_rate_limited(f'sub_rl_ip:{ip}', SUB_RATE_LIMIT_IP, SUB_RATE_LIMIT_IP_PERIOD):
        logger.warning('rate limit hit for IP %s', ip)
        context['error'] = RATE_LIMIT_MESSAGE
        return respond(status=429)

    if not form.is_valid():
        # Log which trap fired, if any, so we can see whether they do any work.
        codes = [e.code for e in form.non_field_errors().as_data()]
        if codes:
            logger.warning('rejected submission from IP %s (%s)', ip, ', '.join(codes))
        return respond()

    email = form.cleaned_data['email']
    if is_rate_limited(f'sub_rl_email:{email.lower()}', SUB_RATE_LIMIT_EMAIL, SUB_RATE_LIMIT_EMAIL_PERIOD):
        logger.warning('rate limit hit for email %s', email)
        context['error'] = RATE_LIMIT_MESSAGE
        return respond(status=429)

    # Checked before the write, so a storm creates no rows either.
    if is_rate_limited('sub_rl_global', SUB_GLOBAL_LIMIT, SUB_GLOBAL_PERIOD):
        logger.error('global send limit reached; dropping signup for %s', email)
        alert_admin_once()
        context['error'] = RATE_LIMIT_MESSAGE
        return respond(status=429)

    sub, created = Subscription.objects.get_or_create(email=email)
    if created or not sub.is_active:
        send_confirmation_email(request, sub)
        send_mail(f'mnmnwag: sub requested by {sub.email} [eom]', '', None, [settings.ADMINS[0][1]])
    else:
        context['already_active'] = True
    context['email'] = sub.email
    return respond()


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
