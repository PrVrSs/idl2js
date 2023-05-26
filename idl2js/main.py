from itertools import chain
from pathlib import Path
from typing import Optional, Union

import click
from click import Context, Option, Parameter

from .transpiler import Transpiler
from .utils import save


def _idl_files(_: Context, __: Union[Option, Parameter], value: Optional[str]) -> tuple[str, ...]:
    if value is None:
        return ()

    return tuple(map(str, Path(value).rglob('*.webidl')))


@click.command()
@click.option(
    '-f', '--file',
    multiple=True,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help='',
)
@click.option(
    '-d', '--directory',
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    callback=_idl_files,
    help='',
)
@click.option(
    '-o', '--output',
    type=click.Path(dir_okay=False, resolve_path=True),
    default='/dev/stdout',
    help='',
)
def cli(file: tuple[str, ...], directory: tuple[str, ...], output: str) -> None:
    save(
        file_name=output,
        content=Transpiler(idls=tuple(chain(file, directory))).transpile()
    )
