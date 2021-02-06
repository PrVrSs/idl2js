from itertools import chain
from pathlib import Path
from typing import Optional, Tuple

import click
from click import Context, Option

from .core import Idl2Js
from .logger import LOG_LEVELS, configure_logging


def _idl_files(_: Context, __: Option, value: Optional[str]) -> Tuple[str, ...]:
    if value is None:
        return ()

    return tuple(map(str, Path(value).rglob('*.webidl')))


def _prepare_output_dir(_: Context, __: Option, value: Optional[str]) -> Optional[str]:
    if value is not None:
        Path(value).resolve().mkdir(parents=True, exist_ok=True)

    return value


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
    type=click.Path(file_okay=False, resolve_path=True),
    callback=_prepare_output_dir,
    default='.output',
    help='',
)
@click.option(
    '-l', '--level',
    default='debug',
    type=click.Choice(LOG_LEVELS.keys()),
    help='',
)
def cli(file: Tuple[str, ...], directory: Tuple[str, ...], output: str, level: str) -> None:
    configure_logging(level)

    Idl2Js(
        idl=tuple(chain(file, directory)),
        output=output,
    )
