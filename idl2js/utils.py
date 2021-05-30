import json
import uuid
from pathlib import Path

import attr


def dump_js(variables, file='tmp.json'):
    with open(file, 'w') as fp:
        json.dump(
            obj=[attr.asdict(variable) for variable in variables],
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


def unique_name():
    return f'v_{uuid.uuid4().hex}'


def save(file_name, content):
    with open(Path(file_name), 'w') as file:
        file.write('\n'.join(content))
