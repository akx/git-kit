from collections import defaultdict
from .util import get_lines


def parse_git_status_lines(status_lines):
    out = defaultdict(list)
    for line in status_lines:
        out[line[:2]].append(line[3:])
    return out


def get_git_status(cmdline):
    return parse_git_status_lines(get_lines(cmdline, strip_left=False))
