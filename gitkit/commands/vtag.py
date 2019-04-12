import datetime

import click

from gitkit.util.cli import yorn, croak
from gitkit.util.shell import run, get_lines


@click.command()
@click.option('--version', '-v', required=True)
def vtag(version):
    """ Create a version commit and release tag. """
    grep_output = list(get_lines(['git', 'grep', version], ignore_errors=True))
    if not grep_output:
        croak('The string %r does not appear in the current code. It should!' % version)

    last_commits = get_lines([
        'git',
        'log',
        '--oneline',
        '-n 10',
    ])
    if not any(version in line for line in last_commits):
        print('None of the last 10 commits contain %r in their commit message.' % version)
        commit_message = "Become %s" % version
        if yorn("Create a %r commit?" % commit_message):
            run(['git', 'commit', '-m', commit_message])

    tag_name = 'v%s' % version
    tag_message = 'Version %s' % version

    if yorn("Will create tag %r with message %r. Okay?" % (tag_name, tag_message)):
        run([
            "git",
            "tag",
            "-a",
            "-m",
            tag_message,
            tag_name,
        ])
        print("Tag %s created." % tag_message)
    else:
        print("No tag was created.")
