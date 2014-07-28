import click
from .util import get_output, get_lines, run
from .conf import sacred_branches

@click.argument('branches', nargs=-1)
def sb(branches):
	""" Set the given branch refs to point to the current HEAD. """
	if not branches:
		print "No branches passed."
		return
	current = get_output("git rev-parse HEAD")
	for branch in branches:
		run(["git", "update-ref", "refs/heads/%s" % branch, current])
		print branch, "set to", current

@click.argument('ref', required=False, default="master")
def del_merged(ref):
	for branch in set(get_lines(["git", "branch", "-l", "--merged", ref])):
		if branch != ref and branch not in sacred_branches:
			run(["git", "branch", "-v", "-d", branch])


def install(cli):
	cli.command()(sb)
	cli.command()(del_merged)
