import click

from gitkit.conf import sacred_branches
from gitkit.util.refs import get_main_branch
from gitkit.util.shell import get_lines, run


@click.command()
@click.argument("ref", required=False, default=None)
def del_merged(ref):
    """
    Delete merged branches.
    """
    if not ref:
        ref = get_main_branch()
    for branch in set(get_lines(["git", "branch", "-l", "--merged", ref])):
        branch = branch.strip("* ")
        if branch != ref and branch not in sacred_branches:
            run(["git", "branch", "-v", "-d", branch])
