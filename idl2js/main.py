from pprint import pprint

import click

from idl2js.core import Idl2Js


@click.command()
@click.option('--webidl', '-w',
              required=True,
              type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def cli(file):
    pprint(Idl2Js(file).generate())
