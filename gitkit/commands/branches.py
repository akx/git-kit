import re

import click

from gitkit.util.shell import get_lines, run


@click.command()
def branches():
    """
    Interactively select a branch.
    """
    reflog_entries = list(
        get_lines(
            [
                "git",
                "log",
                "-g",
                "--pretty=format:%H:%ar:%gs",
                "--grep-reflog=moving from",
            ],
        ),
    )
    branch_options = []
    extant_branches = set(
        line.strip("* ") for line in get_lines(["git", "branch", "--column=plain"])
    )

    for reflog_entry in reflog_entries[:100]:
        branch_match = re.search("from (.+?) to (.+?)$", reflog_entry)
        prev_branch = branch_match.group(1)
        if prev_branch not in branch_options and prev_branch in extant_branches:
            branch_options.append(prev_branch)

    for i, name in enumerate(branch_options, 1):
        print(f"[{i:2d}] {name}")

    branch_idx = int(input("Checkout which branch? ")) - 1
    if 0 <= branch_idx < len(branch_options):
        branch_name = branch_options[branch_idx]
        print(f"Checking out {branch_name}")
        run(["git", "checkout", branch_name])
