import re

import click

from gitkit.conf import sacred_branches
from gitkit.util.cli import yorn
from gitkit.util.shell import run, get_output, get_lines


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


@click.command()
@click.argument('ref', required=False, default="master")
def del_merged(ref):
    for branch in set(get_lines(["git", "branch", "-l", "--merged", ref])):
        branch = branch.strip("* ")
        if branch != ref and branch not in sacred_branches:
            run(["git", "branch", "-v", "-d", branch])


@click.command()
def go_back():
    current_branch = get_output("git rev-parse --abbrev-ref HEAD").strip()
    reflog_entries = get_lines(
        ["git", "log", "-g", "--pretty=format:%H:%ar:%gs", "--grep-reflog=moving from .* to %s" % current_branch]
    )
    for reflog_entry in reflog_entries:
        branch_match = re.search("from (.+?) to (.+?)$", reflog_entry)
        prev_branch = branch_match.group(1)
        new_branch = branch_match.group(2)

        if prev_branch != new_branch:
            if yorn("Checkout %s?" % prev_branch):
                run(["git", "checkout", prev_branch])
                break


@click.command()
def branches():
    reflog_entries = list(
        get_lines(
            ["git", "log", "-g", "--pretty=format:%H:%ar:%gs", "--grep-reflog=moving from"]
        )
    )
    branch_options = []
    extant_branches = set(l.strip("* ") for l in get_lines(["git", "branch", "--column=plain"]))

    for reflog_entry in reflog_entries[:100]:
        branch_match = re.search("from (.+?) to (.+?)$", reflog_entry)
        prev_branch = branch_match.group(1)
        if prev_branch not in branch_options and prev_branch in extant_branches:
            branch_options.append(prev_branch)

    for i, name in enumerate(branch_options, 1):
        print("[%2d] %s" % (i, name))

    branch_idx = int(input("Checkout which branch? ")) - 1
    if 0 <= branch_idx < len(branch_options):
        branch_name = branch_options[branch_idx]
        print("Checking out %s" % branch_name)
        run(["git", "checkout", branch_name])
