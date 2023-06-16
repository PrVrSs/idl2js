import json
import uuid
from contextlib import suppress
from dataclasses import asdict
from pathlib import Path
from typing import Any


def dump_js(variables, file: str = 'tmp.json'):
    with open(file, 'w', encoding='utf-8') as fp:
        json.dump(
            obj=[
                asdict(variable)
                for variable in variables
            ],
            fp=fp,
            indent=4,
        )


def interleave(iterable, func, separator):
    it = iter(iterable)

    try:
        func(next(it))
    except StopIteration:
        pass
    else:
        for item in it:
            separator()
            func(item)


def unique_name() -> str:
    return f'v_{uuid.uuid4().hex}'


def project_idl_list() -> list[str]:
    return [
        str(file)
        for file in (Path(__file__).parent / 'webidls').resolve().glob('*.webidl')
    ]


def save(file_name: str, content: list[str]) -> None:
    with open(Path(file_name), 'w', encoding='utf-8') as file:
        file.write('\n'.join(content))


def read_file(file: str) -> str:
    return Path(file).resolve().read_text(encoding='utf-8')


def is_hashable(value: Any) -> bool:
    with suppress(TypeError):
        hash(value)
        return True

    return False
