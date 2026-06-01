import pytest
from django.conf import settings as django_settings
from django.db import connection
from django.test import Client

# The real (non-test) name of the default database, captured at import time --
# i.e. before any test in this session can trigger pytest-django's test-database
# setup. Once any test uses the standard `db` fixture, Django creates a
# `test_<name>` database and repoints connection['default'] at it for the rest
# of the process. read_only_db has to reach past that hijack to the real dev DB
# that actually holds the pages, so it needs to know the original name.
_REAL_DB_NAME = django_settings.DATABASES['default']['NAME']


@pytest.fixture
def read_only_db(django_db_blocker, settings):
    """
    Grant access to the existing default database in read-only mode.

    Uses django_db_blocker directly so django_db_setup is never called and no
    test database is created. Tests that need a writable test database should
    use the standard `db` fixture instead.

    If some other test in the session *did* use `db`, the default connection now
    points at the (empty) test database; we temporarily swap it back to the real
    database so the page-rendering assertions see real content. The swap is
    reverted on teardown so pytest-django's own DB teardown still targets the
    test database.

    Uses signed_cookies session backend so that session writes (e.g. from
    BlogPageMixin) don't attempt DB inserts against the read-only connection.
    """
    settings.SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

    with django_db_blocker.unblock():
        hijacked_name = connection.settings_dict['NAME']
        swapped = hijacked_name != _REAL_DB_NAME
        if swapped:
            # Drop the test-DB connection and re-point at the real database;
            # the next cursor() lazily reconnects to it.
            connection.close()
            connection.settings_dict['NAME'] = _REAL_DB_NAME

        try:
            with connection.cursor() as cursor:
                cursor.execute('SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY')
            try:
                yield
            finally:
                with connection.cursor() as cursor:
                    cursor.execute('SET SESSION CHARACTERISTICS AS TRANSACTION READ WRITE')
        finally:
            if swapped:
                connection.close()
                connection.settings_dict['NAME'] = hijacked_name


@pytest.fixture
def madprops_client(read_only_db):
    """
    A test Client pointed at the madprops site, using whatever hostname is
    configured in the database (varies between dev/prod envs).
    """
    from wagtail.models import Site
    hostname = Site.objects.get(hostname__icontains='madprops').hostname
    return Client(SERVER_NAME=hostname)
