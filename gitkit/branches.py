import click
import re
from .util import get_output, get_lines, run, yorn
from .conf import sacred_branches


@click.argument('branches', nargs=-1)
def point_here(branches):
    """ Set the given branch refs to point to the current HEAD. """
    if not branches:
        print "No branches passed."
        return
    current = get_output("git rev-parse HEAD")
    for branch in branches:
        run(["git", "update-ref", "refs/heads/%s" % branch, current])
        print branch, "set to", current


@click.argument('ref', required=False, default="master")
def del_merged(ref):
    for branch in set(get_lines(["git", "branch", "-l", "--merged", ref])):
        branch = branch.strip("* ")
        if branch != ref and branch not in sacred_branches:
            run(["git", "branch", "-v", "-d", branch])


def go_back():
    current_branch = get_output("git rev-parse --abbrev-ref HEAD").strip()
    reflog_entries = get_lines(
        ["git", "log", "-g", "--pretty=format:%H:%ar:%gs", "--grep-reflog=moving from .* to %s" % current_branch])
    for reflog_entry in reflog_entries:
        branch_match = re.search("from (.+?) to (.+?)$", reflog_entry)
        prev_branch = branch_match.group(1)
        new_branch = branch_match.group(2)

        if prev_branch != new_branch:
            if yorn("Checkout %s?" % prev_branch):
                run(["git", "checkout", prev_branch])
                break


def install(cli):
    cli.command()(point_here)
    cli.command()(del_merged)
    cli.command()(go_back)
