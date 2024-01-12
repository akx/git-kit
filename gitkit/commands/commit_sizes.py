import re
from collections import namedtuple

import click

from gitkit.util.shell import get_output

shortstat_re = re.compile(
    r"^ (\d+) files? changed, (\d+) insertions?\(\+\), (\d+) deletions?\(-\)$",
)


class ShortStat(namedtuple("_ShortStat", ("files", "insertions", "deletions"))):
    @property
    def total(self) -> int:
        return self.insertions - self.deletions

    @property
    def abs_total(self) -> int:
        return abs(self.insertions) + abs(self.deletions)


@click.command()
def commit_sizes():
    commit_size_map = {}
    commit_id = None
    for line in get_output("git log --shortstat --pretty=format:'...%H=%s'").splitlines():
        if not line:
            continue
        if line.startswith("..."):
            commit_id = tuple(line[3:].split("=", 1))
            continue
        elif line.startswith(" "):
            match = shortstat_re.match(line)
            if match:
                commit_size_map[commit_id] = ShortStat(*(int(x) for x in match.groups()))
    for (commit_id, subject), shortstat in sorted(
        commit_size_map.items(), key=lambda x: x[1].abs_total, reverse=True,
    ):
        short_commit_id = commit_id[:10]
        print(
            f"{short_commit_id} | {subject[:40]:40} | {shortstat.files:5d} | "
            f"{shortstat.insertions:7d} | {-shortstat.deletions:+7d} | Δ {shortstat.total:+7d} | Σ {shortstat.abs_total:7d}",
        )
