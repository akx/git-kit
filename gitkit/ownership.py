# -- encoding: UTF-8 --
from collections import Counter
import json
import re
import time
import sys

from gitkit.util import get_lines

INVALID_RE = re.compile("(jpg|jpeg|css|png|gif|dat|ds_store|ttf|woff|eot|svg|psd)$", re.I)

class OwnershipMachine(object):
    def __init__(self):
        self.blob_blame_cache = {}

    def is_ownable_type(self, path):
        path = unicode(path).lower()
        if INVALID_RE.search(path):
            return False
        if "/migrations/" in path:
            return False
        if "vendor/" in path:
            return False
        return True

    def blame_lines(self, commit, path):
        lines_by_author = Counter()
        for line in get_lines(["git", "blame", "-w", "-M", "-C", "--line-porcelain", commit, "--", path]):
            if line.startswith("author "):
                lines_by_author[line.split(" ", 1)[1]] += 1
        return dict(lines_by_author)

    def process_commit(self, last_commit, commit):
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

        print >>sys.stderr, "%s: %s files" % (commit, len(paths))

        blob_blames = {}
        for path, sha in paths.iteritems():
            blob_blame = self.blob_blame_cache.get(sha)
            if not blob_blame:
                blob_blame = self.blame_lines(commit, path)
                self.blob_blame_cache[sha] = blob_blame
            blob_blames[sha] = blob_blame

        for blob_blame in blob_blames.values():
            for author, n_lines in blob_blame.iteritems():
                lines_by_author[unicode(author)] += n_lines
        return lines_by_author


    def calculate(self, ref):
        commits = {}
        for line in get_lines(["git", "log", "--pretty=format:%at %H", ref]):
            time_str, hash = line.split()
            date = time.strftime("%Y-%m-%d", time.gmtime(int(time_str)))
            commits[date] = hash

        print "Gathered", len(commits), "days of history"

        lines_by_author_per_day = {}

        last_commit = None
        for i, (date, commit) in enumerate(sorted(commits.iteritems())):
            if i % 5:
                continue
            print >>sys.stderr, "Processing commit %d / %d..." % (i, len(commits))
            lines_by_author = self.process_commit(last_commit, commit)
            lines_by_author_per_day[date] = lines_by_author
            print json.dumps({"date": date, "commit": str( commit), "owners": dict(lines_by_author), "total": sum(lines_by_author.values())})
            last_commit = commit

def ownership(ref="master"):
    om = OwnershipMachine()
    om.calculate(ref)

def install(cli):
    cli.command()(ownership)
