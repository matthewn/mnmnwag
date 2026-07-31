"""
Modernize the zoom links hard-coded into LegacyPost bodies.

The blosxom import carried in markup written for Unpoly 2:

    <a up-modal=".zoom" href="/zoom/old/...">

Unpoly 3 dropped [up-modal] in favor of [up-layer="new modal"], and does not
list it as a follow selector, so since the 2->3 upgrade these have been inert --
the browser just follows the href and loads the zoom as a full page. Rewriting
the attribute makes them open in an overlay again.

One image is deliberately left alone: /zoom/old/images/fw10-11.jpg is missing
from the media tree entirely, and its path predates the media/legacy/ prefix, so
zoom_old rejects it. Three posts link to it. Modernizing those would turn a
full-page 403 into an overlaid one, which is not an improvement; they stay as
they are until the file turns up or the links are edited by hand.

Page bodies and their revisions are both rewritten. Wagtail serves the live
field, but the editor loads the latest revision -- leaving revisions untouched
would mean opening one of these posts in the admin and saving it would quietly
restore the Unpoly 2 markup.
"""
import re

from django.db import migrations

OLD_ATTR = 'up-modal=".zoom"'
NEW_ATTR = 'up-layer="new modal"'

# the one link whose target no longer exists; see the module docstring
SKIP_HREF = '/zoom/old/images/fw10-11.jpg'

ANCHOR = re.compile(r'<a\b[^>]*>')


def _swap(body, old, new):
    """
    Swap one attribute for another, but only on anchors that carry it and do not
    point at the missing image. Returns (body, number_of_anchors_changed).
    """
    if not body or old not in body:
        return body, 0

    changed = 0

    def fix(match):
        nonlocal changed
        tag = match.group(0)
        if old not in tag or SKIP_HREF in tag:
            return tag
        changed += 1
        return tag.replace(old, new)

    return ANCHOR.sub(fix, body), changed


def _rewrite(apps, old, new):
    LegacyPost = apps.get_model('mnmnwag', 'LegacyPost')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Revision = apps.get_model('wagtailcore', 'Revision')

    for post in LegacyPost.objects.filter(body__contains=old):
        body, changed = _swap(post.body, old, new)
        if changed:
            post.body = body
            post.save(update_fields=['body'])

    # Revisions store the page's fields as JSON; the body lives under 'body'.
    content_type = ContentType.objects.filter(
        app_label='mnmnwag', model='legacypost',
    ).first()
    if content_type is None:
        return

    revisions = Revision.objects.filter(content_type=content_type)
    for revision in revisions.iterator():
        body = (revision.content or {}).get('body')
        if not body:
            continue
        body, changed = _swap(body, old, new)
        if changed:
            revision.content['body'] = body
            revision.save(update_fields=['content'])


def forwards(apps, schema_editor):
    _rewrite(apps, OLD_ATTR, NEW_ATTR)


def backwards(apps, schema_editor):
    _rewrite(apps, NEW_ATTR, OLD_ATTR)


class Migration(migrations.Migration):

    dependencies = [
        ('mnmnwag', '0054_alter_complexpage_body_alter_modernpost_body'),
        # the migration that gives Revision its content_type, which this filters on
        ('wagtailcore', '0071_populate_revision_content_type'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
