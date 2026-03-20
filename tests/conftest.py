import pytest
from django.db import connection


@pytest.fixture
def read_only_db(django_db_blocker):
    """Grant access to the existing database in read-only mode.

    Uses django_db_blocker directly so django_db_setup is never called and no
    test database is created. Tests that need a writable test database should
    use the standard `db` fixture instead.
    """
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            cursor.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
        try:
            yield
        finally:
            with connection.cursor() as cursor:
                cursor.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ WRITE")
