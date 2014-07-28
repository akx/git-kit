import click
from .util import get_output, run, get_lines, croak, yorn
from .status import get_git_status


def autofixup():
	stati = get_git_status(["git", "status", "--porcelain"])
	changed = stati["M "]
	if not changed:
		unstaged = stati[" M"]
		if len(unstaged) > 1:
			return croak("You haven't staged any changes I can deal with, but you have more than one unstaged file. I can't help you.")
		if not unstaged:
			return croak("Doesn't look like you have any changes autofixup can deal with.")
		if len(unstaged) == 1:
			if yorn("There's one unstaged change (%s) -- would you like to add that and then see if we can autofixup?" % unstaged[0]):
				print "Okay!"
				run(["git", "add", unstaged[0]])
				changed = unstaged

	if len(changed) > 1:
		croak("Not sure where to autofixup when more than one files have changed. :(")

	logline = get_output(["git", "log", "-1", "--format=format:%H: %an, %ar -- %s", changed[0]]).strip()
	if not logline:
		return croak("Could not find any commit that would have touched %s" % changed[0])

	commit = logline.split(":")[0]

	current_parent = get_output(["git", "rev-parse", "HEAD"])

	if commit == current_parent:
		if yorn("Fixup onto %s? -- looks like it's HEAD, so we can just commit --amend. That okay?" % logline):
			run(["git", "commit", "--amend", "--no-edit"])
			print "Amend done."
			return
		else:
			print "Okay, well, we can also fixup..."

	if yorn("Fixup onto %s?" % logline):
		run(["git", "commit", "--fixup", commit])
		print "Fixup done. Remember to `git rebase -i master` or whatever! :)"
	else:
		print "No fixup."


def install(cli):
	cli.command()(autofixup)
