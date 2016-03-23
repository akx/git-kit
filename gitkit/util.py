import subprocess
import sys

import click

REQUIRES_SHELL = (sys.platform != "win32")

def run(command):
    subprocess.check_call(command)


def get_output(command, ignore_errors=False, strip_left=True, strip_right=True):
    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, shell=REQUIRES_SHELL)
    output = pipe.communicate()[0]
    if strip_left:
        output = output.lstrip()
    if strip_right:
        output = output.rstrip()
    if not ignore_errors:
        if pipe.returncode != 0:
            raise subprocess.CalledProcessError(pipe.returncode, pipe.args)
    try:
        output = output.decode("UTF-8")
    except UnicodeError:
        pass
    return output


def get_lines(command, ignore_errors=False, strip_left=True, strip_right=True):
    for line in get_output(command, ignore_errors=ignore_errors, strip_left=False, strip_right=False).splitlines():
        if strip_left:
            line = line.lstrip()
        if strip_right:
            line = line.rstrip()

        if line:
            yield line


def yorn(prompt):
    return click.confirm(prompt)


def croak(message):
    print(message)
    sys.exit(1)
