import click

from gitkit.util.shell import get_output, run


@click.command()
@click.argument('branches', nargs=-1)
def point_here(branches):
    """ Set the given branch refs to point to the current HEAD. """
    if not branches:
        print("No branches passed.")
        return
    current = get_output("git rev-parse HEAD")
    for branch in branches:
        run(["git", "update-ref", "refs/heads/%s" % branch, current])
        print(branch, "set to", current)
