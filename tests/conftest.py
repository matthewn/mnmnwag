import pytest
from django.db import connection


@pytest.fixture
def read_only_db(django_db_blocker, settings):
    """Grant access to the existing database in read-only mode.

    Uses django_db_blocker directly so django_db_setup is never called and no
    test database is created. Tests that need a writable test database should
    use the standard `db` fixture instead.

    Uses signed_cookies session backend so that session writes (e.g. from
    BlogPageMixin) don't attempt DB inserts against the read-only connection.
    """
    settings.SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            cursor.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
        try:
            yield
        finally:
            with connection.cursor() as cursor:
                cursor.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ WRITE")
