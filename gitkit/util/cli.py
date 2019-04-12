import sys

import click


def yorn(prompt):
    return click.confirm(prompt)


def croak(message):
    print(message)
    sys.exit(1)
