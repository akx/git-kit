import os
import re
import shlex

import click

from gitkit.util.shell import get_lines


def get_line_changes(file_path, *, extra_args):
    if not os.path.exists(file_path):
        return

    for line in get_lines(["git", "diff", "-U0", *extra_args, file_path]):
        match = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
        if match:
            start_line = int(match.group(1))
            if match.group(2):
                line_count = int(match.group(2))
                if line_count > 0:
                    yield (start_line, start_line + line_count - 1)
            else:
                yield (start_line, start_line)


@click.command()
@click.option("--ruff-format/--no-ruff-format", default=False)
@click.option("--cached/--no-cached", default=False)
def changed_line_ranges(*, ruff_format: bool, cached: bool):
    extra_args = ["--cached"] if cached else []
    for file_path in get_lines(["git", "diff", "--name-only", *extra_args]):
        if not file_path:
            continue
        line_changes = get_line_changes(file_path, extra_args=extra_args)
        if line_changes:
            for start, end in line_changes:
                if ruff_format:
                    if start == end:
                        print(f"ruff format --range={start} {shlex.quote(file_path)}")
                    else:
                        print(f"ruff format --range={start}-{end} {shlex.quote(file_path)}")
                else:
                    if start == end:
                        print(f"{file_path}\t{start}")
                    else:
                        print(f"{file_path}\t{start}-{end}")
        else:
            print(f"{file_path}\tNo line changes", file=sys.stderr)
