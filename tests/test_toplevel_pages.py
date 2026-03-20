import pytest
from django.test import Client


@pytest.mark.parametrize("url", ["/", "/blog/", "/museyroom/", "/about/"])
def test_mnmnwag_page_renders(read_only_db, url):
    response = Client().get(url)
    assert response.status_code == 200


@pytest.mark.parametrize("url", ["/", "/manifesto/", "/archives/"])
def test_madprops_page_renders(read_only_db, url):
    response = Client(SERVER_NAME="madprops.localhost").get(url)
    assert response.status_code == 200
