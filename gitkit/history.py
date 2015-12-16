import click

from .util import get_output, get_lines


@click.argument('ref1')
@click.argument('range', required=False)
@click.option('-w', is_flag=True, default=False)
@click.option('--diff-params', default="")
def archaeology(ref1, range=None, w=False, diff_params=None):
    ref1 = get_output("git rev-parse %s" % ref1)
    if range:
        refs_in_range = list(get_lines("git log --pretty=%%H %s" % range))
    else:
        refs_in_range = list(get_lines("git log --pretty=%H --all"))

    if ref1 in refs_in_range:
        refs_in_range.remove(ref1)

    diff_params = ("--numstat %s %s" % (diff_params or "", "-w" if w else "")).strip()

    best_ref = None
    best_score = 0
    scores = {}

    def show_best(x):
        if best_ref:
            return "Best found: %s (%d)" % (best_ref[:8], best_score)

    with click.progressbar(refs_in_range, item_show_func=show_best) as refs:
        for ref in refs:
            diff = [l.split("\t") for l in get_lines("git diff-tree %s %s %s" % (diff_params, ref, ref1))]
            delta_lines = sum(int(l[0]) + int(l[1]) for l in diff if not (l[0] == "-" or l[1] == "-"))
            scores[ref] = delta_lines
            if not best_ref or delta_lines < best_score:
                best_ref = ref
                best_score = delta_lines
    print("Best results:")
    for ref, score in sorted(scores.items(), key=lambda pair: pair[1])[:10]:
        print("%32s\t%5d\t%s" % (ref, score, get_output("git describe --all %s" % ref)))


def install(cli):
    cli.command()(archaeology)
