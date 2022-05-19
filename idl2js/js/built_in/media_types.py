import csv
from pathlib import Path


ANY: str = '*'
MIME_SOURCES: Path = (Path(__file__).parent / 'mime').resolve()


def media_types():
    """https://www.iana.org/assignments/media-types/media-types.xml"""
    return {
        file.stem: list(_read(str(file)))
        for file in MIME_SOURCES.glob('*.csv')
    }


def _read(file: str):
    with open(file, encoding='utf-8', newline='') as csv_file:
        for row in csv.DictReader(csv_file):
            if not row['Template']:
                continue

            yield row['Name']
