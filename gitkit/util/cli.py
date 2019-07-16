import sys

import click


def yorn(prompt, default=False):
    return click.confirm(prompt, default=default)


def croak(message):
    print(message)
    sys.exit(1)
