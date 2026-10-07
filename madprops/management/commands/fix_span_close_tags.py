"""
Repair malformed closing tags left in stored rich text by the old yes/no
Draftail features, which wrote `</span class="yes">` and `</span class="no">`.

Walks every StreamField and RichTextField in the project, plus page
revisions, and replaces the bad closing tags with `</span>`.
"""

from django.apps import apps
from django.core.management.base import BaseCommand
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Revision

import json

BAD_TAGS = ('</span class="yes">', '</span class="no">')
# the same tags as they appear inside a JSON-encoded string (revisions store
# StreamField bodies as JSON strings nested inside the revision's JSON)
BAD_TAGS_ESCAPED = tuple(json.dumps(tag)[1:-1] for tag in BAD_TAGS)


def fix_html(text):
    for tag in BAD_TAGS + BAD_TAGS_ESCAPED:
        text = text.replace(tag, '</span>')
    return text


def fix_json(data):
    """ Fix every string nested anywhere in JSON-compatible data. """
    if isinstance(data, str):
        return fix_html(data)
    if isinstance(data, list):
        return [fix_json(item) for item in data]
    if isinstance(data, dict):
        return {key: fix_json(value) for key, value in data.items()}
    return data


class Command(BaseCommand):
    help = 'replace </span class="yes"> and </span class="no"> with </span> in stored rich text'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='report what would change without saving anything',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        total = 0

        for model in apps.get_models():
            # local_fields only, so multi-table subclasses don't get visited twice
            for field in model._meta.local_fields:
                if isinstance(field, StreamField):
                    total += self.fix_streamfield(model, field)
                elif isinstance(field, RichTextField):
                    total += self.fix_richtextfield(model, field)

        total += self.fix_revisions()

        verb = 'would fix' if self.dry_run else 'fixed'
        self.stdout.write(self.style.SUCCESS(f'{verb} {total} record(s)'))

    def report(self, label, pk):
        self.stdout.write(f'{label} pk={pk}')

    def fix_streamfield(self, model, field):
        count = 0
        for obj in model.objects.all().iterator():
            old = list(getattr(obj, field.name).raw_data)
            new = fix_json(old)
            if new == old:
                continue
            count += 1
            self.report(f'{model._meta.label}.{field.name}', obj.pk)
            if not self.dry_run:
                # update() skips save() so no new revisions or signals fire
                model.objects.filter(pk=obj.pk).update(**{field.name: new})
        return count

    def fix_richtextfield(self, model, field):
        count = 0
        for obj in model.objects.all().iterator():
            old = getattr(obj, field.name) or ''
            new = fix_html(old)
            if new == old:
                continue
            count += 1
            self.report(f'{model._meta.label}.{field.name}', obj.pk)
            if not self.dry_run:
                model.objects.filter(pk=obj.pk).update(**{field.name: new})
        return count

    def fix_revisions(self):
        count = 0
        for rev in Revision.objects.all().iterator():
            new = fix_json(rev.content)
            if new == rev.content:
                continue
            count += 1
            self.report('wagtailcore.Revision', rev.pk)
            if not self.dry_run:
                Revision.objects.filter(pk=rev.pk).update(content=new)
        return count
