import click, importlib

@click.group()
def cli():
    pass

for modname in ("gitkit.branches", "gitkit.tags", "gitkit.commits", "gitkit.ownership"):
    module = importlib.import_module(modname)
    getattr(module, "install")(cli)

if __name__ == '__main__':
    cli()
