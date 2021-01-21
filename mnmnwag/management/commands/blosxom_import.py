from django.core.management.base import BaseCommand

import os
import time


TARGET_DIR = '/home/matthewn/working/01_PERSONAL/blosxom_data'


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        for (root, dirs, files) in os.walk(TARGET_DIR):
            path = root.replace(TARGET_DIR, '')
            tag = path.split('/')[-1]
            for filename in files:
                if filename.endswith('.blog'):
                    filepath = os.path.join(root, filename)
                    with open(filepath, 'r') as f:
                        post = f.readlines()

                    old_path = os.path.join(path, filename)
                    title = post[0][0:-1]
                    # body = '\r'.join(post[1:])
                    created = time.ctime(os.path.getmtime(filepath))
                    has_comments = os.path.exists(filepath.replace('.blog', '.wb'))

                    print(f'{old_path} {created} {tag} {title}')
                    # print(body)
                    if has_comments:
                        print('HAS COMMENTS!!!!!!')
