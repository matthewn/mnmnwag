"""
Import posts and comments from a blosxom blog with the writebacks plugin.

Converts blosxom categories to tags.

Assumes that TARGET_DIR is a directory tree containing blosxom blog posts
(in .blog files) with writeback files (.wb) alongside them.
"""

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from wagtail.core.models import Page
from mnmnwag.models import LegacyPost

import datetime as dt
import os
import re

PARENT_PAGE_ID = 4
TARGET_DIR = '/home/matthewn/working/01_PERSONAL/blosxom_data'


class Command(BaseCommand):
    help = 'import a directory tree of blosxom and writeback files'

    def handle(self, *args, **options):
        for (dirname, subdirs, files) in os.walk(TARGET_DIR):
            for filename in files:
                if filename.endswith('5books.blog'):  # FIXME
                    filepath = os.path.join(dirname, filename)

                    page = self.build_page(filepath)
                    self.publish_page(**page)

                    # does this post have comments?
                    has_comments = os.path.exists(filepath.replace('.blog', '.wb'))

                    if has_comments:
                        with open(filepath.replace('.blog', '.wb')) as f:
                            writebacks = f.readlines()
                        comments = self.get_comments(writebacks)
                        if comments:
                            # print(comments)
                            pass

    def build_page(self, filepath):
        page = {}
        with open(filepath, 'r') as f:
            post = f.readlines()
        # get post title
        page['title'] = post[0][0:-1]
        # convert old filename to new slug
        page['slug'] = filepath.split('/')[-1].replace('.blog', '').replace('_', '-')
        # get post creation datetime
        page['created'] = make_aware(dt.datetime.fromtimestamp(os.path.getmtime(filepath)))
        # get old relative URL (for redirects on new site)
        page['old_path'] = filepath.replace(TARGET_DIR, '').replace('.blog', '.html')
        # get wagtail tag (tail directory from path)
        page['tag'] = filepath.split('/')[-2]
        # get body
        page['body'] = '\r'.join(post[1:])
        return page

    def publish_page(self, title, slug, created, old_path, tag, body):
        # print(f'\n{title}\n{slug}\n{created}\n{old_path}\n{tag}\n{body[:200]} ...')
        print(title)
        parent_page = Page.objects.get(id=PARENT_PAGE_ID).specific
        page = LegacyPost(  # foooo
            title=title,
            body=body,
            old_path=old_path,
            slug=slug,
            has_comments_enabled=False,
            first_published_at=created,
        )
        page.tags.add(tag)
        page.tags.add('from-blosxom')
        parent_page.add_child(instance=page)
        page.save_revision().publish()

    def get_comments(self, writebacks):
        """
        Return a list of dictionaries, each one containing a comment
        for a post.
        """
        comments = []  # holds all comments
        comment = {}   # holds one comment
        for line in writebacks:
            if '-----' not in line:
                # store this line's data in the dictionary
                regex = '^(.*): (.*)\n'
                match = re.search(regex, line)
                if match and match.group(2) != '':
                    comment[match.group(1)] = match.group(2)
            else:
                # we have reached the end of a comment, so add it
                # to the dictionary and start a new one
                comments.append(comment)
                comment = {}
        return comments
