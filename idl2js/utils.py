import attr
import json


def dump_js(variables, file='tmp.json'):
    with open(file, 'w') as f:
        json.dump(
            obj=[attr.asdict(variable) for variable in variables],
            fp=f,
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
