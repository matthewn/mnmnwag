from django.core.management.base import BaseCommand

from mnmnwag.models import ModernPost
from subs.models import SubscriptionsTracker
from subs.utils import send_notifications


class Command(BaseCommand):
    help = 'send email notifications about new posts'

    def handle(self, *args, **options):
        tracker = SubscriptionsTracker.load()
        posts = ModernPost.objects.live().filter(
            first_published_at__gte=tracker.last_run_at
        )
        if posts:
            send_notifications(posts)
        tracker.save()
