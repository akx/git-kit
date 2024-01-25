import click

from gitkit.util.shell import get_output


def get_commit_subject(ref):
    return get_output(
        [
            "git",
            "log",
            "-n1",
            "--pretty=format:%s",
            ref,
        ],
    )


@click.command()
def annotate_blame_ignores():
    out_lines = []
    current_header = []
    with open(".git-blame-ignore-revs") as f:
        for line in f:
            line = line.strip()
            if not line:
                current_header.clear()
                out_lines.append(line)
                continue
            if line.startswith("#"):
                current_header.append(line)
                continue
            if line.isalnum():  # likely a commit hash
                if not current_header:
                    subj = get_commit_subject(line)
                    current_header = ["", f"# {subj}"]
                out_lines.extend(current_header)
                current_header.clear()
                out_lines.append(line)
                continue
            out_lines.append(line)
    while out_lines and not out_lines[0]:
        out_lines.pop(0)
    for line in out_lines:
        print(line)
