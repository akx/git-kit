import re

import click

from gitkit.util.cli import yorn
from gitkit.util.shell import get_output, run

ssh_url_re = re.compile(r"git@(?P<host>.+?):(?P<path>.+)")


@click.command()
@click.option("--pull-only/--no-pull-only", "-p", default=False, help="only change the pull URL")
def httpify_remote(pull_only: bool):
    """
    HTTP-ify remote SSH URLs.
    """
    remote_configs = dict(
        line.split("=", 1)
        for line in get_output("git config -l").splitlines()
        if line.startswith("remote.")
    )

    remote_urls = {k.split(".")[1]: v for k, v in remote_configs.items() if k.endswith(".url")}

    found = False
    for remote, url in remote_urls.items():
        if not ssh_url_re.match(url):
            continue
        found = True
        new_url = ssh_url_re.sub(r"https://\g<host>/\g<path>", url)
        old_url_bold = click.style(url, bold=True)
        new_url_bold = click.style(new_url, bold=True)
        remote_bold = click.style(remote, bold=True)
        if pull_only:
            if yorn(
                f"Change {remote_bold} pull URL from {old_url_bold} to {new_url_bold} "
                f"(and set push URL to {old_url_bold})?",
            ):
                run(["git", "remote", "set-url", "--push", remote, url])
                run(["git", "remote", "set-url", remote, new_url])
        else:
            if yorn(
                f"Change {remote_bold} from {old_url_bold} to {new_url_bold}?",
            ):
                run(["git", "remote", "set-url", remote, new_url])

    if not found:
        click.echo("No SSH URLs found.")
