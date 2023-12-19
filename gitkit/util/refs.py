from gitkit.conf import main_branch_candidates

from .shell import get_lines


def get_branches():
    for branch in get_lines(["git", "branch", "-l"]):
        yield branch.strip("* ")


def get_main_branch():
    for branch in get_branches():
        if branch in main_branch_candidates:
            return branch
    raise ValueError("Could not find main branch")
