import pytest
from django.test import Client


@pytest.mark.parametrize("url", ["/", "/blog/", "/museyroom/", "/about/"])
def test_page_renders(read_only_db, url):
    response = Client().get(url)
    assert response.status_code == 200
