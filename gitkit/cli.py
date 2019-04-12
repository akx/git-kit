import importlib
import os
import pkgutil

import click


@click.group()
def cli():
    pass


def initialize():
    commands_dir = os.path.join(os.path.dirname(__file__), "commands")
    for _, name, _ in pkgutil.iter_modules([commands_dir]):
        module = importlib.import_module("gitkit.commands.%s" % name)
        for name, value in vars(module).items():
            try:
                if isinstance(value, click.Command):
                    cli.add_command(value)
            except TypeError:
                pass


initialize()
