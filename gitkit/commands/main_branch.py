import click

from gitkit.util.refs import get_main_branch


@click.command()
def main_branch():
    """
    Print out the name of the main branch, for scripting purposes.
    """
    print(get_main_branch())
