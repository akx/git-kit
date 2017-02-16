import importlib
import os
import pkgutil

import click
from click import Command


@click.group()
def cli():
    pass


def initialize():
    dir = os.path.dirname(__file__)
    for _, name, _ in pkgutil.iter_modules([dir]):
        if name in ('cli', 'conf', 'util'):
            continue
        module = importlib.import_module('gitkit.%s' % name)
        for name, value in vars(module).items():
            try:
                if isinstance(value, Command):
                    cli.add_command(value)
            except TypeError:
                pass


initialize()
