import os
import re
from typing import Match
from urllib.parse import urljoin

from . import settings, utils

URL_PATTERN = re.compile(
    r"""
    url\(
    \s*      # any amount of whitespace
    ([\'"]?) # optional quote
    (.*?)    # any amount of anything, non-greedily (this is the actual url)
    \1       # matching quote (or nothing if there was none)
    \s*      # any amount of whitespace
    \)""",
    re.VERBOSE,
)


def convert_url(url: str, source_dir: str) -> str:
    assert source_dir[-1] == "/"

    url = url.strip()
    if not url:
        return url

    if not url.startswith(("http://", "https://", "/", "data:", "#")):
        url = urljoin(settings.STATIC_URL, urljoin(source_dir, url))

    return url


def convert(content: str, path: str) -> str:
    source_dir = os.path.dirname(path)
    if not source_dir.endswith("/"):
        source_dir += "/"

    def url_converter(matchobj: Match[str]) -> str:
        quote = matchobj.group(1)
        converted_url = convert_url(matchobj.group(2), source_dir)
        return f"url({quote}{converted_url}{quote})"

    return URL_PATTERN.sub(url_converter, content)


def convert_urls(compiled_full_path: str, source_path: str) -> None:
    content = utils.read_file(compiled_full_path)
    converted_content = convert(content, source_path)
    utils.write_file(converted_content, compiled_full_path)
