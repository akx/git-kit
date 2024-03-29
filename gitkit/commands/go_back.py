import re

import click

from gitkit.util.cli import yorn
from gitkit.util.shell import get_lines, get_output, run


@click.command()
def go_back():
    """
    Go back to a previous ref.
    """
    current_branch = get_output("git rev-parse --abbrev-ref HEAD").strip()
    reflog_entries = get_lines(
        [
            "git",
            "log",
            "-g",
            "--pretty=format:%H:%ar:%gs",
            f"--grep-reflog=moving from .* to {current_branch}",
        ],
    )
    for reflog_entry in reflog_entries:
        branch_match = re.search("from (.+?) to (.+?)$", reflog_entry)
        prev_branch = branch_match.group(1)
        new_branch = branch_match.group(2)

        if prev_branch != new_branch:
            if yorn(f"Checkout {prev_branch}?"):
                run(["git", "checkout", prev_branch])
                break
