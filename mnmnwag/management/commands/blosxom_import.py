"""
Import posts and comments from a blosxom blog with the writebacks plugin.

Converts blosxom categories to tags.

Assumes that TARGET_DIR is a directory tree containing blosxom blog posts
(in .blog files) with writeback files (.wb) alongside them.
"""

from django.core.management.base import BaseCommand

import os
import re
import time


TARGET_DIR = '/home/matthewn/working/01_PERSONAL/blosxom_data'


class Command(BaseCommand):
    help = 'import a directory tree of blosxom and writeback files'

    def handle(self, *args, **options):
        for (dirname, subdirs, files) in os.walk(TARGET_DIR):
            # get original relative site path
            path = dirname.replace(TARGET_DIR, '')
            # wagtail tag is tail directory from path
            tag = path.split('/')[-1]

            for filename in files:
                if filename.endswith('.blog'):
                    filepath = os.path.join(dirname, filename)
                    with open(filepath, 'r') as f:
                        post = f.readlines()

                    # get post title
                    title = post[0][0:-1]
                    # convert old filename to new slug
                    slug = filename.replace('.blog', '').replace('_', '-')
                    # get post creation datetime
                    created = time.ctime(os.path.getmtime(filepath))
                    # get old relative URL (for redirects on new site)
                    old_url = os.path.join(path, filename).replace('.blog', '.html')
                    # get body
                    body = '\r'.join(post[1:])
                    # does this post have comments?
                    has_comments = os.path.exists(filepath.replace('.blog', '.wb'))

                    print(f'\n{title}\n{slug}\n{created}\n{old_url}\n{tag}\n{body[:200]} ...')

                    if has_comments:
                        with open(filepath.replace('.blog', '.wb')) as f:
                            writebacks = f.readlines()
                        comments = self.get_comments(writebacks)
                        if comments:
                            print(comments)

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
