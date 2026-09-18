import time

from django import forms
from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

from honeypot.decorators import honeypot_equals

# A form submitted faster than this many seconds after it was served was
# almost certainly not filled in by a human.
MIN_FORM_AGE = 3

# ...and one submitted later than this is a stale page or a replayed capture.
MAX_FORM_AGE = 60 * 60 * 4

# Deliberately vague: never tell a bot which of our traps it tripped.
REJECTION_MESSAGE = 'Your submission could not be verified. Please reload the page and try again.'

signer = TimestampSigner(salt='subs.forms')


def make_timestamp():
    """
    Return a signed, tamper-proof record of when a form was served.
    """
    return signer.sign(str(int(time.time())))


def unsign_timestamp(value):
    """
    Return the unix time the given signed timestamp says the form was served,
    raising BadSignature if it is forged, malformed, or too old.

    The age is read from the signed payload, so the one value we render into
    the form is the single source of truth for how old that form is. (unsign()
    is given max_age too, but only as a backstop: for timestamps we issued
    ourselves the two clocks are the same one, a second apart at most.)
    """
    served_at = signer.unsign(value, max_age=MAX_FORM_AGE)
    try:
        served_at = int(served_at)
    except ValueError:
        raise BadSignature('non-numeric timestamp payload') from None
    if time.time() - served_at > MAX_FORM_AGE:
        raise SignatureExpired('timestamp payload too old')
    return served_at


class SubscriptionForm(forms.Form):
    """
    Subscription signup, guarded by three cheap anti-bot checks: a honeypot
    field, a minimum/maximum time-to-submit, and (in the view) rate limiting.

    Every failure mode raises the same generic error, so a bot learns nothing
    about which check caught it.
    """

    email = forms.EmailField(
        label='your email address:',
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Please enter a valid email address.',
        },
        widget=forms.EmailInput(attrs={'placeholder': 'reader@example.org'}),
    )
    timestamp = forms.CharField(max_length=100, widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The honeypot field name is configurable, so it has to be added at
        # runtime rather than declared. Bots fill in every field they see;
        # humans never see this one (the template keeps it hidden).
        self.fields[settings.HONEYPOT_FIELD_NAME] = forms.CharField(
            label='',
            required=False,
            widget=forms.TextInput(attrs={'autocomplete': 'off', 'tabindex': '-1'}),
        )

    @property
    def timestamp_value(self):
        """
        The signed timestamp to render into the form.

        Reuses the incoming one when it's still good, so a human correcting a
        typo keeps their original (already old enough) timestamp, but issues a
        fresh one when it's missing, forged, or expired -- otherwise a visitor
        who left the page open would be stuck failing forever.
        """
        if self.is_bound:
            try:
                unsign_timestamp(self.data.get('timestamp', ''))
            except BadSignature:
                pass
            else:
                return self.data['timestamp']
        return make_timestamp()

    @property
    def honeypot(self):
        """
        The honeypot bound field, for templates that don't know its name.
        """
        return self[settings.HONEYPOT_FIELD_NAME]

    def clean(self):
        cleaned_data = super().clean()
        self.check_honeypot(cleaned_data)
        self.check_timestamp(cleaned_data)
        return cleaned_data

    def check_honeypot(self, cleaned_data):
        """
        Reject the form if anything was typed into the hidden field -- or if
        the field is missing altogether, which means the submitter built the
        POST body themselves instead of fetching our form.
        """
        verifier = getattr(settings, 'HONEYPOT_VERIFIER', honeypot_equals)
        field_name = settings.HONEYPOT_FIELD_NAME
        if field_name not in self.data or not verifier(cleaned_data.get(field_name, '')):
            raise forms.ValidationError(REJECTION_MESSAGE, code='honeypot')

    def check_timestamp(self, cleaned_data):
        """
        Reject the form if it was submitted implausibly fast, or so long after
        it was served that it's likely a replay of a harvested form body.

        A missing or forged signature is rejected too: the signature is what
        stops a bot from simply inventing a plausible-looking timestamp.
        """
        try:
            served_at = unsign_timestamp(cleaned_data.get('timestamp', ''))
        except BadSignature:
            raise forms.ValidationError(REJECTION_MESSAGE, code='timestamp') from None
        if time.time() - served_at < MIN_FORM_AGE:
            raise forms.ValidationError(REJECTION_MESSAGE, code='too_fast')
