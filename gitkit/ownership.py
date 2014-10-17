# -- encoding: UTF-8 --
from collections import Counter
import json
import re
import time

from gitkit.util import get_lines


INVALID_RE = re.compile("(jpg|jpeg|css|png|gif)$", re.I)

def is_ownable_type(path):
    path = unicode(path).lower()
    if INVALID_RE.search(path):
        return False
    if "/migrations/" in path:
        return False
    return True

def blame_lines(commit, path):
    lines_by_author = Counter()
    for line in get_lines(["git", "blame", "--line-porcelain", commit, "--", path]):
        if line.startswith("author "):
            lines_by_author[line.split(" ", 1)[1]] += 1
    return dict(lines_by_author)


def process_commit(commit):
    blob_blames = {}
    lines_by_author = Counter()
    for line in get_lines(["git", "ls-tree", "-r", commit]):
        line = line.strip()
        if line:
            line = line.split()
            mode, kind, sha, path = line
            if kind == "blob":
                if is_ownable_type(path):
                    blob_blames[sha] = blame_lines(commit, path)
    for blob_blame in blob_blames.values():
        for author, n_lines in blob_blame.iteritems():
            lines_by_author[unicode(author)] += n_lines
    return lines_by_author


def ownership(ref="master"):
    commits = {}
    for line in get_lines(["git", "--no-pager", "log", "--pretty=format:%at %H", ref]):
        time_str, hash = line.split()
        date = time.strftime("%Y-%m-%d", time.gmtime(int(time_str)))
        commits[date] = hash

    print "Gathered", len(commits), "days of history"

    lines_by_author_per_day = {}

    for date, commit in sorted(commits.iteritems()):
        lines_by_author = process_commit(commit)
        lines_by_author_per_day[date] = lines_by_author
        print json.dumps({"date": date, "commit": str( commit), "owners": dict(lines_by_author), "total": sum(lines_by_author.values())})


def install(cli):
    cli.command()(ownership)
