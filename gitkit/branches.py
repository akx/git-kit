import click
from .util import run

@click.argument('branches', nargs=-1)
def sb(branches):
	""" Set the given branch refs to point to the current HEAD. """
	if not branches:
		print "No branches passed."
		return
	current = run("git rev-parse HEAD")
	for branch in branches:
		run(["git", "update-ref", "refs/heads/%s" % branch, current])
		print branch, "set to", current

def install(cli):
	cli.command()(sb)