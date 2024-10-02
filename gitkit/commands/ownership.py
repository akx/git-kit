# -- encoding: UTF-8 --
import json
import sys
import time
from collections import Counter
from multiprocessing.pool import ThreadPool

import click

from gitkit.util.shell import get_lines, get_output

INVALID_SUFFIXES = (
    ".css",
    ".dat",
    ".deb",
    ".ds_store",
    ".eot",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".po",  # committer generally isn't the author of a language file
    ".pot",  # committer generally isn't the author of a language file
    ".psd",
    ".snap",
    ".svg",
    ".ttf",
    ".woff",
    "package-lock.json",
    "package.json",
    "pnpm-lock.yaml",
    "yarn.lock",
)


def count_lines_by_author(blob_blames):
    lines_by_author = Counter()
    for blob_blame in list(blob_blames.values()):
        for author, n_lines in blob_blame.items():
            lines_by_author[str(author)] += n_lines
    return lines_by_author


def is_ownable_type(path):
    path = str(path).lower()
    if path.endswith(INVALID_SUFFIXES):
        return False
    if "/migrations/" in path:
        return False
    if "vendor/" in path:
        return False
    return True


def get_path_to_sha_map(commit):
    paths = {}
    for line in get_lines(["git", "ls-tree", "-r", commit]):
        line = line.strip()
        if line:
            line = line.split(None, 3)
            _mode, kind, sha, path = line
            if kind == "blob":
                if is_ownable_type(path):
                    paths[path] = sha
    return paths


def blame_lines(commit, path):
    lines_by_author = Counter()
    for line in get_lines(
        ["git", "blame", "-w", "-M", "-C", "--line-porcelain", commit, "--", path],
        strip_left=False,
    ):
        if line.startswith("author "):
            lines_by_author[line.partition("author ")[2]] += 1
    return dict(lines_by_author)


class OwnershipMachine(object):
    def __init__(self):
        self.blob_blame_cache = {}

    def process_commit(self, commit, progress=False):
        paths = get_path_to_sha_map(commit)

        print(f"{commit}: {len(paths)} files", file=sys.stderr)

        def _cached_get_blob_blame(pair):
            path, sha = pair
            blob_blame = self.blob_blame_cache.get(sha)
            if not blob_blame:
                blob_blame = blame_lines(commit, path)
                self.blob_blame_cache[sha] = blob_blame
            return (pair, blob_blame)

        blob_blames = {}
        with ThreadPool() as pool:
            work_item_iterator = click.progressbar(
                iterable=(pool.imap_unordered(_cached_get_blob_blame, paths.items())),
                length=len(paths),
                item_show_func=lambda i: (i[0][0] if i else None),
            )
            work_item_iterator.is_hidden = not progress
            with work_item_iterator:
                for (path, sha), result in work_item_iterator:
                    blob_blames[sha] = result

        return count_lines_by_author(blob_blames)

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
            print(f"Processing commit {i} / {len(commits)}...", file=sys.stderr)
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
def ownership(ref="HEAD", step=5, over_time=False):
    """
    Figure out total authorship, line-by-line, of the repository.
    """
    om = OwnershipMachine()
    if over_time:
        for datum in om.calculate_over_time(ref, step=step):
            print(json.dumps(datum))
    else:
        commit = get_output(f"git rev-parse {ref}")
        print(f"Processing commit {commit}...", file=sys.stderr)
        lines_by_author = om.process_commit(commit, progress=True)
        print(
            json.dumps(
                {
                    "owners": dict(sorted(lines_by_author.items(), key=lambda x: x[1], reverse=True)),
                    "total": sum(lines_by_author.values()),
                },
                ensure_ascii=False,
            ),
        )
