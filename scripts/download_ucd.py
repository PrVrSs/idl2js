"""Script for create `ucd.json`"""

import json
import tempfile
import urllib.request
import zipfile
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path

from lxml import etree


URL = 'https://unicode.org/Public/UCD/latest/ucdxml/ucd.all.flat.zip'
FILE_NAME = 'ucd.all.flat.xml'
DESTINATION = (Path(__file__).parent.parent / 'idl2js' / 'generators' / 'ucd.json').resolve()

CHAR_ELEMENT_PATH = etree.XPath(
    '//ucd:char',
    namespaces={'ucd': 'http://www.unicode.org/ns/2003/ucd/1.0'},
)


def read_ucd_xml(xml: bytes) -> dict[str, list[int]]:
    result = defaultdict(list)
    for char in CHAR_ELEMENT_PATH(etree.XML(xml)):
        if char.get('gc') is None:
            continue

        if char.get('cp') is None:
            continue

        result[char.get('gc')].append(int(char.get('cp'), base=16))

    return result


def download(url: str) -> bytes:
    with urllib.request.urlopen(url) as response:
        return response.read()

@contextmanager
def create_zip_file(data: bytes) -> str:
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(data)
        yield tmp.name


def unzip(filename: str) -> dict[str, bytes]:
    with zipfile.ZipFile(filename, 'r') as fp:
        return {
            name: fp.read(name)
            for name in fp.namelist()
        }


def save(data: dict[str, list[int]], filename: str = 'ucd.json') -> None:
    with open(filename, 'w') as fp:
        json.dump(data, fp)


def prepare_ucd(data: bytes) -> dict[str, list[int]]:
    with create_zip_file(data=data) as filename:
        return read_ucd_xml(xml=unzip(filename=filename)[FILE_NAME])


def main() -> None:
    ucd_raw = download(url=URL)

    save(
        data=dict(prepare_ucd(ucd_raw)),
        filename=str(DESTINATION),
    )


if __name__ == '__main__':
    main()
