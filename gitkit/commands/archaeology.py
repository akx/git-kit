from subprocess import CalledProcessError

import click

from gitkit.util.shell import get_output, get_lines


@click.command()
@click.argument("ref1")
@click.argument("range", required=False)
@click.option("-w", is_flag=True, default=False, help="ignore whitespace?")
@click.option("--diff-params", default="")
def archaeology(ref1, range=None, w=False, diff_params=None):
    """
    Find a commit most closely resembling a ref.
    """
    ref1 = get_output(f"git rev-parse {ref1}")
    if range:
        refs_in_range = list(get_lines(f"git log --pretty=%%H {range}"))
    else:
        refs_in_range = list(get_lines("git log --pretty=%H --all"))

    if ref1 in refs_in_range:
        refs_in_range.remove(ref1)

    diff_params = (f"--numstat {diff_params or ''} {'-w' if w else ''}").strip()

    best_ref = None
    best_score = 0
    scores = {}

    def show_best(x):
        if best_ref:
            return f"Best found: {best_ref[:8]} ({best_score:d})"

    with click.progressbar(refs_in_range, item_show_func=show_best) as refs:
        for ref in refs:
            try:
                diff = [
                    l.split("\t")
                    for l in get_lines(
                        f"git -c core.safecrlf=off diff-tree {ref} {ref1} {diff_params}"
                    )
                ]
            except CalledProcessError:
                continue
            delta_lines = sum(
                int(l[0]) + int(l[1]) for l in diff if not (l[0] == "-" or l[1] == "-")
            )
            scores[ref] = delta_lines
            if not best_ref or delta_lines < best_score:
                best_ref = ref
                best_score = delta_lines
    print("Best results:")
    for ref, score in sorted(list(scores.items()), key=lambda pair: pair[1])[:10]:
        description = get_output(f"git describe --all --always {ref}")
        print(f"{ref:>32}\t{score:5d}\t{description}")
