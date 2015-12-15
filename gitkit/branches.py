import click
import re
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
    reflog_entries = get_lines(
        ["git", "log", "-g", "--pretty=format:%H:%ar:%gs", "--grep-reflog=moving from .* to %s" % current_branch])
    for reflog_entry in reflog_entries:
        branch_match = re.search("from (.+?) to (.+?)$", reflog_entry)
        prev_branch = branch_match.group(1)
        new_branch = branch_match.group(2)

        if prev_branch != new_branch:
            if yorn("Checkout %s?" % prev_branch):
                run(["git", "checkout", prev_branch])
                break

def branches():
    reflog_entries = list(
        get_lines(
            ["git", "log", "-g", "--pretty=format:%H:%ar:%gs", "--grep-reflog=moving from"]
        )
    )
    branch_options = []
    extant_branches = set(l.strip("* ") for l in get_lines(["git", "branch", "--column=plain"]))

    for reflog_entry in reflog_entries[:100]:
        branch_match = re.search("from (.+?) to (.+?)$", reflog_entry)
        prev_branch = branch_match.group(1)
        if prev_branch not in branch_options and prev_branch in extant_branches:
            branch_options.append(prev_branch)

    for i, name in enumerate(branch_options, 1):
        print "[%2d] %s" % (i, name)

    branch_idx = int(raw_input("Checkout which branch? ")) - 1
    if 0 <= branch_idx < len(branch_options):
        branch_name = branch_options[branch_idx]
        print "Checking out %s" % branch_name
        run(["git", "checkout", branch_name])


@click.argument('ref1')
@click.argument('range', required=False)
def archaeology(ref1, range=None):
    ref1 = get_output("git rev-parse %s" % ref1)
    if range:
        refs_in_range = list(get_lines("git log --pretty=%%H %s" % range))
    else:
        refs_in_range = list(get_lines("git log --pretty=%H --all"))

    if ref1 in refs_in_range:
        refs_in_range.remove(ref1)

    best_ref = None
    best_score = 0
    scores = {}

    def show_best(x):
        if best_ref:
            return "Best found: %s (%d)" % (best_ref[:8], best_score)

    with click.progressbar(refs_in_range, item_show_func=show_best) as refs:
        for ref in refs:
            diff = [l.split("\t") for l in get_lines("git diff-tree --numstat %s %s" % (ref, ref1))]
            delta_lines = sum(int(l[0]) + int(l[1]) for l in diff if not (l[0] == "-" or l[1] == "-"))
            scores[ref] = delta_lines
            if not best_ref or delta_lines < best_score:
                best_ref = ref
                best_score = delta_lines
    print("Best results:")
    for ref, score in sorted(scores.items(), key=lambda pair: pair[1])[:10]:
        print("%32s\t%5d\t%s" % (ref, score, get_output("git describe --all %s" % ref)))


def install(cli):
    cli.command()(point_here)
    cli.command()(del_merged)
    cli.command()(go_back)
    cli.command()(branches)
    cli.command()(archaeology)
