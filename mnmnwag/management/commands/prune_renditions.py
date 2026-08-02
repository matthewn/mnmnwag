import os

from django.core.management.base import BaseCommand
from django.template.defaultfilters import filesizeformat
from wagtail.images import get_image_model


class Command(BaseCommand):
    help = (
        'Find rendition files on disk that no rendition record points at -- '
        'leftovers from renditions the site no longer generates, or from '
        'images that have been deleted. Lists them and totals their size; '
        'pass --delete to actually remove them.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete the orphaned files instead of just listing them.',
        )

    def handle(self, *args, **options):
        image_model = get_image_model()
        rendition_model = image_model.get_rendition_model()
        storage = rendition_model.file.field.storage

        # Where renditions live, per the rendition model itself ('images/' out
        # of the box) -- ask it rather than hardcoding the path.
        directory = os.path.dirname(rendition_model().get_upload_to('x.jpg'))

        # Originals live elsewhere, but should a stray one ever land in the
        # rendition directory we must not mistake it for garbage.
        in_use = set(rendition_model.objects.values_list('file', flat=True))
        in_use |= set(image_model.objects.values_list('file', flat=True))

        orphans = sorted(
            path for path in self._walk(storage, directory) if path not in in_use
        )

        total = 0
        for path in orphans:
            try:
                size = storage.size(path)
            except OSError as e:
                self.stderr.write(f'{path}: {e}')
                continue
            total += size
            if options['delete']:
                try:
                    storage.delete(path)
                except OSError as e:
                    self.stderr.write(f'{path}: {e}')
                    total -= size
                    continue
            else:
                self.stdout.write(path)

        if not orphans:
            self.stdout.write(self.style.SUCCESS('No orphaned renditions found.'))
            return

        verb = 'Deleted' if options['delete'] else 'Found'
        count = len(orphans)
        plural = '' if count == 1 else 's'
        self.stdout.write(self.style.SUCCESS(
            f'{verb} {count} orphaned rendition file{plural}, '
            f'{filesizeformat(total)}.'
        ))

    def _walk(self, storage, directory):
        """
        Yield the storage paths of every file at or below directory.
        """
        directories, files = storage.listdir(directory)
        for filename in files:
            yield os.path.join(directory, filename)
        for subdirectory in directories:
            yield from self._walk(storage, os.path.join(directory, subdirectory))
