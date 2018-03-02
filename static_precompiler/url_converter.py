import os
import re

from django.utils import six

from . import settings, utils

if six.PY2:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from urlparse import urljoin
else:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from urllib.parse import urljoin

URL_PATTERN = re.compile(r"url\(([^\)]+)\)(?=;)")


def convert_url(url, source_dir):
    assert source_dir[-1] == "/"

    url = url.strip()
    if not url:
        return url

    original_quote = url[0] if url[0] in ('"', "'") else "'"
    url = url.strip("\"'")

    if not url.startswith(('http://', 'https://', '/', 'data:')):
        url = urljoin(settings.STATIC_URL, urljoin(source_dir, url))

    return "{original_quote}{url}{original_quote}".format(original_quote=original_quote, url=url)


def convert(content, path):
    source_dir = os.path.dirname(path)
    if not source_dir.endswith("/"):
        source_dir += "/"

    return URL_PATTERN.sub(
        lambda matchobj: "url({0})".format(
            convert_url(matchobj.group(1), source_dir)
        ),
        content
    )


def convert_urls(compiled_full_path, source_path):
    content = utils.read_file(compiled_full_path)
    converted_content = convert(content, source_path)
    utils.write_file(converted_content, compiled_full_path)
