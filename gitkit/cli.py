import importlib

import click


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
