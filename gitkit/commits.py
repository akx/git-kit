from .status import get_git_status
from .util import croak, get_output, run, yorn


def autofixup():
    stati = get_git_status(["git", "status", "--porcelain"])
    changed = _autofixup_get_changed_files(stati)
    if len(changed) > 1:
        croak("Not sure where to autofixup when more than one files have changed. :(")

    logline = get_output(["git", "log", "-1", "--format=format:%H: %an, %ar -- %s", ":/" + changed[0]]).strip()
    if not logline:
        return croak("Could not find any commit that would have touched %s" % changed[0])

    commit = logline.split(":")[0]

    current_parent = get_output(["git", "rev-parse", "HEAD"])

    if commit == current_parent:
        if yorn("Fixup onto %s? -- looks like it's HEAD, so we can just commit --amend. That okay?" % logline):
            run(["git", "commit", "--amend", "--no-edit"])
            return print("Amend done.")
        print("Okay, well, we can also fixup...")

    if yorn("Fixup onto %s?" % logline):
        run(["git", "commit", "--fixup", commit])
        return print("Fixup done. Remember to `git rebase -i master` or whatever! :)")
    print("No fixup.")


def _autofixup_get_changed_files(stati):
    changed = stati["M "] or stati["MM"]
    if not changed:
        unstaged = stati[" M"]
        if len(unstaged) > 1:
            croak(
                "You haven't staged any changes I can deal with, "
                "but you have more than one unstaged file. I can't help you.")
        if not unstaged:
            croak("Doesn't look like you have any changes autofixup can deal with.")
        if len(unstaged) == 1:
            if yorn(
                    "There's one unstaged change (%s) -- "
                    "would you like to add that and then see if we can autofixup?" %
                    unstaged[0]
            ):
                print("Okay!")
                run(["git", "add", ":/" + unstaged[0]])
                changed = unstaged
    return changed


def what():
    description = get_output("git describe")
    revision = get_output("git rev-parse HEAD")
    print(("%s (%s)" % (description, revision)))


def install(cli):
    cli.command()(autofixup)
    cli.command()(what)
