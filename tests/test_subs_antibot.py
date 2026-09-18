import time
from unittest.mock import patch

import pytest
from django.conf import settings
from django.core import mail
from django.core.cache import cache
from django.test import Client
from django.urls import reverse

from subs.forms import MAX_FORM_AGE, MIN_FORM_AGE, SubscriptionForm, make_timestamp, signer
from subs.models import Subscription
from subs.views import SUB_RATE_LIMIT_EMAIL, SUB_RATE_LIMIT_IP

HONEYPOT = settings.HONEYPOT_FIELD_NAME


def old_timestamp(age):
    """
    A validly signed timestamp claiming the form was served `age` seconds ago.
    """
    return signer.sign(str(int(time.time()) - age))


def tampered_timestamp():
    """
    A genuine signed timestamp whose payload has been edited to look older.
    """
    good = make_timestamp()
    return str(int(time.time()) - 600) + good[good.index(':'):]


def post_data(email='reader@example.org', age=MIN_FORM_AGE + 1, **overrides):
    """
    A submission that passes every anti-bot check unless `overrides` says otherwise.

    An override of None drops the field entirely, to simulate a bot that built
    the POST body itself rather than fetching our form.
    """
    data = {'email': email, 'timestamp': old_timestamp(age), HONEYPOT: ''}
    data.update(overrides)
    return {k: v for k, v in data.items() if v is not None}


def error_codes(form):
    """
    The `code` of each non-field error raised by validating `form`.
    """
    form.is_valid()
    return [e.code for e in form.non_field_errors().as_data()]


def client_for(ip):
    """
    A client posting from `ip`, so a test can simulate a rotating IP pool.
    """
    return Client(SERVER_NAME='mahnamahna.test', REMOTE_ADDR=ip)


def proxied_client():
    """
    A client shaped like production: gunicorn on a unix socket leaves
    REMOTE_ADDR empty, and Caddy passes the real address in a header.
    """
    return Client(SERVER_NAME='mahnamahna.test', REMOTE_ADDR='')


def proxied_post(client, ip, email):
    """
    Post as `ip` the way Caddy presents it, rather than as a socket peer.
    """
    return client.post(
        reverse('sub_create'),
        post_data(email=email),
        headers={'x-forwarded-for': ip},
    )


@pytest.fixture
def small_global_limit():
    """
    Shrink the site-wide send cap so tests can trip it in a few requests.
    """
    with patch('subs.views.SUB_GLOBAL_LIMIT', 2):
        yield 2


@pytest.fixture
def sub_client(db, settings):
    """
    A client pointed at a mahnamahna host (sub_create 404s on any other host),
    with a clean cache so rate-limit counters don't leak between tests.
    """
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, 'mahnamahna.test']
    cache.clear()
    yield Client(SERVER_NAME='mahnamahna.test')
    cache.clear()


# ---------------------------------------------------------------------------
# Form validation
# ---------------------------------------------------------------------------

def test_clean_submission_is_valid():
    """
    The baseline: a human leaves the hidden field alone and takes a moment to
    type, and the form validates.
    """
    assert SubscriptionForm(post_data()).is_valid()


@pytest.mark.parametrize(
    ('overrides', 'expected_code'),
    [
        pytest.param({HONEYPOT: 'http://spam.example'}, 'honeypot', id='honeypot-filled'),
        pytest.param({HONEYPOT: None}, 'honeypot', id='honeypot-omitted'),
        pytest.param({'timestamp': None}, 'timestamp', id='timestamp-omitted'),
        pytest.param({'timestamp': str(int(time.time()) - 60)}, 'timestamp', id='timestamp-unsigned'),
        pytest.param({'timestamp': tampered_timestamp()}, 'timestamp', id='timestamp-tampered'),
        pytest.param({'age': MAX_FORM_AGE + 60}, 'timestamp', id='timestamp-expired'),
        pytest.param({'age': 0}, 'too_fast', id='submitted-instantly'),
    ],
)
def test_form_rejects_bot_submission(overrides, expected_code):
    """
    Each trap rejects its own kind of bot: a filled or absent honeypot field,
    a timestamp that is missing, unsigned, forged or expired, and a submission
    that arrives faster than a human could have typed it.

    The unsigned and tampered cases are the point of signing at all -- without
    it a bot could simply invent an old-enough-looking timestamp.
    """
    assert error_codes(SubscriptionForm(post_data(**overrides))) == [expected_code]


# ---------------------------------------------------------------------------
# Timestamp reissue
# ---------------------------------------------------------------------------

def test_unbound_form_issues_fresh_timestamp():
    """
    A freshly served form carries a signed timestamp of roughly right now.
    """
    served_at = int(signer.unsign(SubscriptionForm().timestamp_value))
    assert abs(time.time() - served_at) < 5


def test_bound_form_preserves_valid_timestamp():
    """
    Re-rendering after a validation error keeps the original timestamp, so a
    human fixing a typo isn't pushed back below the minimum age.
    """
    data = post_data(email='not-an-email', age=30)
    form = SubscriptionForm(data)
    form.is_valid()
    assert form.timestamp_value == data['timestamp']


def test_bound_form_replaces_expired_timestamp():
    """
    An expired timestamp is swapped for a fresh one on re-render, so a visitor
    who left the tab open all day isn't stuck failing forever.
    """
    form = SubscriptionForm(post_data(age=MAX_FORM_AGE + 60))
    form.is_valid()
    served_at = int(signer.unsign(form.timestamp_value))
    assert abs(time.time() - served_at) < 5


# ---------------------------------------------------------------------------
# The view: humans
# ---------------------------------------------------------------------------

def test_get_renders_form(sub_client):
    """
    GET serves the form, including the hidden honeypot and timestamp fields.
    """
    response = sub_client.get(reverse('sub_create'))
    assert response.status_code == 200
    content = response.content.decode()
    assert f'name="{HONEYPOT}"' in content
    assert 'name="timestamp"' in content


def test_valid_post_creates_subscription_and_sends_mail(sub_client):
    """
    A clean submission creates an inactive Subscription and sends both the
    confirmation email and the admin notification.
    """
    response = sub_client.post(reverse('sub_create'), post_data())
    assert response.status_code == 200
    sub = Subscription.objects.get(email='reader@example.org')
    assert sub.is_active is False
    assert len(mail.outbox) == 2


def test_repeat_post_for_active_sub_sends_nothing(sub_client):
    """
    An address that is already subscribed and confirmed gets a friendly notice
    and no further email.
    """
    Subscription.objects.create(email='reader@example.org', is_active=True)
    response = sub_client.post(reverse('sub_create'), post_data())
    assert response.context['already_active'] is True
    assert mail.outbox == []


def test_invalid_email_reports_error_and_creates_nothing(sub_client):
    """
    A human typo gets a visible error rather than the silent failure the old
    checkbox captcha gave everyone.
    """
    response = sub_client.post(reverse('sub_create'), post_data(email='nope'))
    assert 'Please enter a valid email address.' in response.content.decode()
    assert Subscription.objects.count() == 0


# ---------------------------------------------------------------------------
# The view: bots get nothing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'overrides',
    [
        pytest.param({HONEYPOT: 'spam'}, id='honeypot-filled'),
        pytest.param({'timestamp': None}, id='timestamp-omitted'),
        pytest.param({'age': 0}, id='submitted-instantly'),
    ],
)
def test_bot_post_creates_nothing(sub_client, overrides):
    """
    Whichever trap fires, the outcome is the same: no Subscription row, no
    email sent, and no clue in the response about what went wrong.
    """
    response = sub_client.post(reverse('sub_create'), post_data(**overrides))
    assert response.status_code == 200
    assert Subscription.objects.count() == 0
    assert mail.outbox == []
    content = response.content.decode().lower()
    assert 'could not be verified' in content
    assert 'honeypot' not in content


def test_rejection_is_logged(sub_client):
    """
    Rejections are logged rather than failing silently, so we can tell whether
    the traps are catching anything.
    """
    with patch('subs.views.logger') as mock_logger:
        sub_client.post(reverse('sub_create'), post_data(**{HONEYPOT: 'spam'}))
    assert mock_logger.warning.called
    assert 'honeypot' in mock_logger.warning.call_args.args


# ---------------------------------------------------------------------------
# The view: rate limiting
# ---------------------------------------------------------------------------

def test_ip_rate_limit_returns_429(sub_client):
    """
    Past SUB_RATE_LIMIT_IP attempts in an hour, an IP is turned away -- even
    with an otherwise perfectly valid submission.
    """
    for i in range(SUB_RATE_LIMIT_IP):
        response = sub_client.post(reverse('sub_create'), post_data(email=f'reader{i}@example.org'))
        assert response.status_code == 200
    response = sub_client.post(reverse('sub_create'), post_data(email='onemore@example.org'))
    assert response.status_code == 429
    assert not Subscription.objects.filter(email='onemore@example.org').exists()


def test_email_rate_limit_returns_429(sub_client):
    """
    A single address can't be used to fire off confirmation emails repeatedly,
    even from different IPs.
    """
    for i in range(SUB_RATE_LIMIT_EMAIL):
        assert client_for(f'10.0.0.{i}').post(reverse('sub_create'), post_data()).status_code == 200
    response = client_for('10.0.0.99').post(reverse('sub_create'), post_data())
    assert response.status_code == 429


def test_bot_attempts_count_against_the_ip_limit(sub_client):
    """
    Failed submissions are counted too, so a bot hammering the traps still
    runs itself out of attempts.
    """
    for _ in range(SUB_RATE_LIMIT_IP):
        sub_client.post(reverse('sub_create'), post_data(**{HONEYPOT: 'spam'}))
    response = sub_client.post(reverse('sub_create'), post_data())
    assert response.status_code == 429
    assert Subscription.objects.count() == 0


# ---------------------------------------------------------------------------
# The view: global circuit breaker
# ---------------------------------------------------------------------------

def signup_from_new_client(i):
    """
    A fresh signup that evades every per-client limit: new IP, new address.
    """
    return client_for(f'10.1.0.{i}').post(reverse('sub_create'), post_data(email=f'reader{i}@example.org'))


def test_global_limit_survives_ip_rotation(sub_client, small_global_limit):
    """
    The per-IP and per-email limits are both walked around by an attacker with
    a proxy pool; the site-wide cap is the one control that still bites.
    """
    for i in range(small_global_limit):
        assert signup_from_new_client(i).status_code == 200
    assert signup_from_new_client(99).status_code == 429


def test_global_limit_stops_sending(sub_client, small_global_limit):
    """
    Past the cap nothing goes out but the one admin alert, and no row is written.
    """
    for i in range(small_global_limit):
        signup_from_new_client(i)
    mail.outbox.clear()
    signup_from_new_client(99)
    assert not Subscription.objects.filter(email='reader99@example.org').exists()
    assert [m.subject for m in mail.outbox] == ['mnmnwag: subscription send limit reached [eom]']


def test_global_limit_alerts_admin_only_once(sub_client, small_global_limit):
    """
    A sustained storm alerts once per period rather than becoming its own flood.
    """
    for i in range(small_global_limit):
        signup_from_new_client(i)
    mail.outbox.clear()
    for i in range(99, 104):
        signup_from_new_client(i)
    assert len(mail.outbox) == 1


# ---------------------------------------------------------------------------
# The view: finding the client behind the proxy
# ---------------------------------------------------------------------------

def test_forwarded_ip_outranks_remote_addr(sub_client):
    """
    One forwarded IP is one bucket even when REMOTE_ADDR differs per request.

    The two candidate keys are made to disagree on purpose: keying on
    REMOTE_ADDR would hand these requests separate buckets and let the second
    through.
    """
    with patch('subs.views.SUB_RATE_LIMIT_IP', 1):
        assert proxied_post(client_for('10.0.0.1'), '203.0.113.7', 'one@example.org').status_code == 200
        response = proxied_post(client_for('10.0.0.2'), '203.0.113.7', 'two@example.org')
    assert response.status_code == 429


def test_distinct_forwarded_ips_get_distinct_buckets(sub_client):
    """
    Two forwarded IPs are two buckets, though their REMOTE_ADDR is identical
    (and empty). Keying on REMOTE_ADDR alone made the per-IP limit a site-wide
    one in production, and no test could see it.
    """
    with patch('subs.views.SUB_RATE_LIMIT_IP', 1):
        assert proxied_post(proxied_client(), '203.0.113.7', 'one@example.org').status_code == 200
        response = proxied_post(proxied_client(), '198.51.100.4', 'two@example.org')
    assert response.status_code == 200
