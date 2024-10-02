import click

from gitkit.util.cli import croak, yorn
from gitkit.util.shell import get_lines, run


@click.command()
@click.option("--version", "-v", required=True)
@click.option("--force/--no-force", "-f")
def vtag(version, force: bool):
    """Create a version commit and release tag."""
    grep_output = list(get_lines(["git", "grep", version], ignore_errors=True))
    if not grep_output:
        msg = f"The string {version!r} does not appear in the current code. It should!"
        if force:
            print(f"Warning: {msg}")
        else:
            croak(msg)

    last_commits = get_lines(["git", "log", "--oneline", "-n 10"])
    if not any(version in line for line in last_commits):
        print(
            f"None of the last 10 commits contain {version!r} in their commit message.",
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
