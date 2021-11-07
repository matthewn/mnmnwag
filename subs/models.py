from django.db import models

from mnmnwag.models import SingletonModel

import uuid


class Subscription(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
    )
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)


class SubscriptionsTracker(SingletonModel):
    last_run_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Subscriptions job tracker'
