import click, re
from .util import get_output, get_lines, run, yorn
from .conf import sacred_branches

@click.argument('branches', nargs=-1)
def point_here(branches):
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
		branch = branch.strip("* ")
		if branch != ref and branch not in sacred_branches:
			run(["git", "branch", "-v", "-d", branch])

def go_back():
	current_branch = get_output("git rev-parse --abbrev-ref HEAD").strip()
	reflog_entry = get_output(["git", "log", "-1", "-g", "--pretty=format:%H:%ar:%gs", "--grep-reflog=moving from .* to %s" % current_branch])
	last_other_branch = re.search("from (.+?) to ", reflog_entry).group(1)
	if yorn("Checkout %s?" % last_other_branch):
		run(["git", "checkout", last_other_branch])


def install(cli):
	cli.command()(point_here)
	cli.command()(del_merged)
	cli.command()(go_back)
