import re

import click

from gitkit.util.cli import yorn
from gitkit.util.shell import get_output, run

ssh_url_re = re.compile(r"git@(?P<host>.+?):(?P<path>.+)")


@click.command()
def httpify_remote():
    """
    HTTP-ify remote SSH URLs.
    """
    remote_configs = dict(
        l.split("=", 1)
        for l
        in get_output("git config -l").splitlines()
        if l.startswith("remote.")
    )

    remote_urls = {
        k.split(".")[1]: v
        for k, v
        in remote_configs.items()
        if k.endswith(".url")
    }

    found = False
    for remote, url in remote_urls.items():
        if ssh_url_re.match(url):
            found = True
            new_url = ssh_url_re.sub(r"https://\g<host>/\g<path>", url)
            if yorn(
                f"Change {click.style(remote, bold=True)} from {click.style(url, bold=True)} to {click.style(new_url, bold=True)}?"):
                run(["git", "remote", "set-url", remote, new_url])

    if not found:
        click.echo("No SSH URLs found.")
