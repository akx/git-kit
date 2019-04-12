# -- encoding: UTF-8 --
import json
import re
import sys
import time
from collections import Counter

import click

from gitkit.util.shell import get_output, get_lines

INVALID_EXTENSIONS = {
    "css",
    "dat",
    "ds_store",
    "eot",
    "gif",
    "jpeg",
    "png",
    "psd",
    "svg",
    "ttf",
    "woff",
    "jpg",
    "deb",
}

INVALID_RE = re.compile("(%s)$" % "|".join(INVALID_EXTENSIONS), re.I)


class OwnershipMachine(object):
    def __init__(self):
        self.blob_blame_cache = {}

    def is_ownable_type(self, path):
        path = str(path).lower()
        if INVALID_RE.search(path):
            return False
        if "/migrations/" in path:
            return False
        if "vendor/" in path:
            return False
        return True

    def blame_lines(self, commit, path):
        lines_by_author = Counter()
        for line in get_lines(
            ["git", "blame", "-w", "-M", "-C", "--line-porcelain", commit, "--", path],
            strip_left=False,
        ):
            if line.startswith("author "):
                lines_by_author[line.split(" ", 1)[1]] += 1
        return dict(lines_by_author)

    def process_commit(self, commit, progress=False):
        paths = {}
        lines_by_author = Counter()
        for line in get_lines(["git", "ls-tree", "-r", commit]):
            line = line.strip()
            if line:
                line = line.split(None, 3)
                mode, kind, sha, path = line
                if kind == "blob":
                    if self.is_ownable_type(path):
                        paths[path] = sha

        print("%s: %s files" % (commit, len(paths)), file=sys.stderr)

        blob_blames = {}
        path_sha_iter = click.progressbar(
            list(paths.items()), item_show_func=lambda i: (i[0] if i else None)
        )
        path_sha_iter.is_hidden = not progress
        with path_sha_iter:
            for path, sha in path_sha_iter:
                blob_blame = self.blob_blame_cache.get(sha)
                if not blob_blame:
                    blob_blame = self.blame_lines(commit, path)
                    self.blob_blame_cache[sha] = blob_blame
                blob_blames[sha] = blob_blame

        for blob_blame in list(blob_blames.values()):
            for author, n_lines in blob_blame.items():
                lines_by_author[str(author)] += n_lines
        return lines_by_author

    def calculate_over_time(self, ref, step=5):
        commits = {}
        for line in get_lines(["git", "log", "--pretty=format:%at %H", ref]):
            time_str, hash = line.split()
            date = time.strftime("%Y-%m-%d", time.gmtime(int(time_str)))
            commits[date] = hash

        print("Gathered", len(commits), "days of history")

        for i, (date, commit) in enumerate(sorted(commits.items())):
            if i % step:
                continue
            print("Processing commit %d / %d..." % (i, len(commits)), file=sys.stderr)
            lines_by_author = self.process_commit(commit)
            day_datum = {
                "date": date,
                "commit": str(commit),
                "owners": dict(lines_by_author),
                "total": sum(lines_by_author.values()),
            }
            yield day_datum


@click.command()
@click.option("--step", type=int, default=5)
@click.option("--over-time/--no-over-time", default=False)
def ownership(ref="master", step=5, over_time=False):
    """
    Figure out total authorship, line-by-line, of the repository.
    """
    om = OwnershipMachine()
    if over_time:
        for datum in om.calculate_over_time(ref, step=step):
            print(json.dumps(datum))
    else:
        commit = get_output("git rev-parse %s" % ref)
        print("Processing commit %s..." % commit, file=sys.stderr)
        lines_by_author = om.process_commit(commit, progress=True)
        print(
            json.dumps(
                {
                    "owners": dict(lines_by_author),
                    "total": sum(lines_by_author.values()),
                }
            )
        )
