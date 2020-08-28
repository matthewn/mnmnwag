from django.dispatch import receiver
from django.db.models.signals import pre_save

from django_comments_xtd.models import XtdComment
from django_comments_xtd.views import notify_comment_followers


@receiver(pre_save, sender=XtdComment)
def send_delayed_notifications(sender, **kwargs):
    """
    Send django_comments_xtd followup notification emails when a comment is
    published.

    Since we have moderation on for all comment submissions, we can safely
    assume that when a comment switches from is_public=False to is_public=True,
    it's been published. So we tell django_comments_xtd to let any followers
    know.

    TODO/FIXME: If the comment is for some reason unpublished and then
    published again, the notifications will get sent again. Hmm.
    """
    if kwargs['instance'].is_public is True:
        current = XtdComment.objects.get(id=kwargs['instance'].id)
        if current.is_public is False:
            # comment is being published, so send notifications
            notify_comment_followers(current)
