from django.db import models

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
