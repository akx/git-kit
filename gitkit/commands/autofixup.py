import click
from collections import namedtuple

from gitkit.util.cli import croak, yorn
from gitkit.util.shell import get_output, run, get_lines
from gitkit.util.status import get_git_status


class AutofixupCommitInfo(
    namedtuple("_CommitInfo", ("commit", "author", "reldate", "subject"))
):
    @property
    def info(self):
        return " / ".join((self.author, self.reldate, self.subject))

    def __str__(self):
        return self.info


@click.command()
def autofixup():
    """
    Attempt to figure out a commit to fix up a single changed file into.
    """
    changed = _autofixup_get_changed_files()
    if len(changed) > 1:
        croak("Not sure where to autofixup when more than one files have changed. :(")

    filename = changed[0]

    afis = [
        AutofixupCommitInfo(*log_line.split(";"))
        for log_line in get_lines(
            [
                "git",
                "log",
                "-n",
                "15",
                "--format=format:%H;%an;%ar;%s",
                "--",
                f":/{filename}",
            ]
        )
    ]
    if not afis:
        return croak(f"Could not find any commit that would have touched {filename}")

    for i, log_line in enumerate(afis, 1):
        click.echo("".join((click.style(f"[{i:2d}] ", bold=True), log_line.info)))

    index = click.prompt(
        f"Choose a commit (1..{len(afis):d})", default=1, type=int, show_default=True
    )
    afi = afis[index - 1]

    current_parent_commit = get_output(["git", "rev-parse", "HEAD"])

    if afi.commit == current_parent_commit:
        if yorn(
            f"Fixup onto {click.style(str(afi), bold=True)}? – looks like it's HEAD, so we can just amend. That okay?",
            default=True,
        ):
            run(["git", "commit", "--amend", "--no-edit"])
            return print("Amend done.")
        print("Okay, well, we can also fixup...")

    if yorn(f"Fixup onto {click.style(str(afi), bold=True)}?", default=True):
        run(["git", "commit", "--fixup", afi.commit])
        return print("Fixup done. Remember to `git rebase -i master` or whatever! :)")
    print("No fixup.")


def _autofixup_get_changed_files():
    stati = get_git_status(["git", "status", "--porcelain"])
    changed = stati["M "] or stati["MM"]
    if not changed:
        unstaged = stati[" M"]
        if len(unstaged) > 1:
            croak(
                "You haven't staged any changes I can deal with, "
                "but you have more than one unstaged file. I can't help you."
            )
        if not unstaged:
            croak("Doesn't look like you have any changes autofixup can deal with.")
        if len(unstaged) == 1:
            if yorn(
                f"There's one unstaged change ({unstaged[0]}) -- "
                f"would you like to add that and then see if we can autofixup?"
            ):
                print("Okay!")
                run(["git", "add", ":/" + unstaged[0]])
                changed = unstaged
    return changed
