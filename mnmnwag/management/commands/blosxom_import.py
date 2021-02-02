"""
Import posts and comments from a blosxom blog with the writebacks plugin.

Converts blosxom categories to tags.

Assumes that TARGET_DIR is a directory tree containing blosxom blog posts
(in .blog files) with writeback files (.wb) alongside them.
"""

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from django_comments_xtd.models import XtdComment
from django.contrib.sites.models import Site
from wagtail.core.models import Page
from wagtail.contrib.redirects.models import Redirect
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
                if filename.endswith('.blog'):
                    filepath = os.path.join(dirname, filename)
                    post = self.get_post(filepath)
                    page = self.publish_page(**post)

                    self.create_redirect(page)

                    has_comments = os.path.exists(filepath.replace('.blog', '.wb'))
                    if has_comments:
                        comments = self.get_comments(filepath.replace('.blog', '.wb'))
                        self.publish_comments(page, comments)

    def get_post(self, filepath):
        """
        Transform a blosxom .blog file into something meaningful.
        Returns a dictionary that we can feed to publish_page().
        """
        post = {}
        with open(filepath, 'r') as f:
            postfile = f.readlines()
        # get title as string w/ no newline
        post['title'] = postfile[0][0:-1]
        # get slug from old filename
        post['slug'] = filepath.split('/')[-1].replace('.blog', '').replace('_', '-')
        # get creation datetime from file modified date
        post['created'] = make_aware(dt.datetime.fromtimestamp(os.path.getmtime(filepath)))
        # get old relative URL (for redirects on new site) from filepath
        post['old_path'] = '/blog' + filepath.replace(TARGET_DIR, '').replace('.blog', '.html')
        # get wagtail tag from final directory in filepath
        post['tag'] = filepath.split('/')[-2]
        # get body as string with newlines
        body = '\n'.join(postfile[1:])
        # rewrite old blog image paths
        body = body.replace('/images/blog/', '/media/legacy/images/blog/')
        # rewrite zoom.py links
        body = body.replace('/cgi-bin/zoom.py?img=/', '/zoom/old/')
        # rewrite zoom shortcut links
        body = body.replace('/img/', '/zoom/old/media/legacy/images/')
        # add some unpoly modal magic to zoom links
        body = body.replace('<a href="/zoom/old/', '<a up-modal=".zoom" href="/zoom/old/')
        post['body'] = body
        return post

    def publish_page(self, title, slug, created, old_path, tag, body):
        """
        Publish a new page in Wagtail.
        """
        parent_page = Page.objects.get(id=PARENT_PAGE_ID).specific
        page = LegacyPost(
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
        self.stdout.write(self.style.SUCCESS(f'\nPublished: {title}'))
        return page

    def create_redirect(self, page):
        """
        Create a wagtail redirect from post's old path to new page.
        """
        Redirect.objects.create(
            old_path=page.old_path,
            site=page.get_site(),
            redirect_page=page,
        )
        self.stdout.write(self.style.SUCCESS(f'Created redirect for: {page.old_path}'))

    def get_comments(self, filepath):
        """
        Given a writebacks file (.wb) containing comments for a post, return a
        list of dictionaries, each one containing a comment.
        """
        comments = []  # holds all comments
        comment = {}   # holds one comment
        with open(filepath, 'r') as f:
            writebacks = f.readlines()
        for line in writebacks:
            if '-----' not in line:
                # store this line's data in the dictionary
                regex = '^(.*?): (.*)\n'
                match = re.search(regex, line)
                if match and match.group(2) != '':
                    comment[match.group(1)] = match.group(2)
            else:
                # we have reached the end of a comment, so make some tweaks to
                # the dictionary, append it to the comments list, and start a
                # new one
                #
                # some comments aren't comments -- they are TRACKBACKS! oh
                # shit, remember those? let's treat them like comments...
                if 'name' not in comment and 'blog_name' in comment:
                    comment['name'] = comment['blog_name']
                    comment['comment'] = comment['excerpt']
                # old 'url' field is really an overloaded email/url field...
                # figure out which we have (if any), assign empty string to
                # fields we don't have
                if 'url' in comment:
                    if 'mailto:' in comment['url']:
                        comment['email'] = comment['url'].replace('mailto:', '')
                        comment['url'] = ''
                    else:
                        comment['email'] = ''
                else:
                    comment['url'] = comment['email'] = ''
                if 'ip' not in comment:
                    comment['ip'] = None
                comments.append(comment)
                comment = {}
        return comments

    def publish_comments(self, page, comments):
        """
        Publish XtdComments with no threading.
        """
        for comment in comments:
            XtdComment.objects.create(
                content_type=page.content_type,
                object_pk=page.id,
                user_name=comment['name'],
                user_email=comment['email'],
                user_url=comment['url'],
                ip_address=comment['ip'],
                comment=comment['comment'],
                submit_date=make_aware(dt.datetime.strptime(comment['date'], '%m/%d/%Y %H:%M:%S')),
                site=Site.objects.get(),
                is_public=True,
            )
            self.stdout.write(self.style.SUCCESS(f"Published comment from: {comment['name']}"))
