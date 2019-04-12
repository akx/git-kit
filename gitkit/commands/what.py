import click

from gitkit.util.shell import get_output


@click.command()
def what():
    """
    What _is_ the current revision anyway?
    """
    description = get_output("git describe")
    revision = get_output("git rev-parse HEAD")
    print(("%s (%s)" % (description, revision)))
