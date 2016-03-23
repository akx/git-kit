import importlib

import click

__version__ = "0.0.1"


@click.group()
def cli():
    pass

for modname in (
    "gitkit.branches",
    "gitkit.commits",
    "gitkit.history",
    "gitkit.ownership",
    "gitkit.tags",
):
    module = importlib.import_module(modname)
    getattr(module, "install")(cli)

if __name__ == '__main__':
    cli()
