import datetime

import click

from gitkit.util.cli import yorn, croak
from gitkit.util.shell import run, get_lines


@click.command()
@click.option("--version", "-v", required=True)
def vtag(version):
    """ Create a version commit and release tag. """
    grep_output = list(get_lines(["git", "grep", version], ignore_errors=True))
    if not grep_output:
        croak(f"The string {version!r} does not appear in the current code. It should!")

    last_commits = get_lines(["git", "log", "--oneline", "-n 10"])
    if not any(version in line for line in last_commits):
        print(
            f"None of the last 10 commits contain {version!r} in their commit message."
        )
        commit_message = f"Become {version}"
        if yorn(f"Create a {commit_message!r} commit?"):
            run(["git", "commit", "-m", commit_message])

    tag_name = f"v{version}"
    tag_message = f"Version {version}"

    if yorn(f"Will create tag {tag_name!r} with message {tag_message!r}. Okay?"):
        run(["git", "tag", "-a", "-m", tag_message, tag_name])
        print(f"Tag {tag_message} created.")
    else:
        print("No tag was created.")
