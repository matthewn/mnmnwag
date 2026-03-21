from unittest.mock import patch

from mnmnwag.templatetags.typefixes import namecloak


def cloak(text, site):
    with patch("mnmnwag.templatetags.typefixes.get_site", return_value=site):
        return namecloak(text)


def test_mnmnwag_replaces_with_html():
    result = cloak("Posted by Matthew Newton.", "mnmnwag")
    assert "Matthew Newton" not in result
    assert '<span class="mahna">' in result


def test_madprops_replaces_with_pseudonym():
    result = cloak("Written by Matthew Newton.", "madprops")
    assert result == "Written by The Mad Propster."


def test_unknown_site_returns_text_unchanged():
    text = "Matthew Newton wrote this."
    assert cloak(text, None) == text


def test_no_name_in_text_unchanged():
    text = "Nothing to see here."
    assert cloak(text, "mnmnwag") == text
