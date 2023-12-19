import collections
import secrets
import statistics

import click

from gitkit.util.shell import get_output


def print_stats(title, lst):
    print(title, "common", collections.Counter(lst).most_common(10))
    print(title, "median", statistics.median(lst))
    print(title, "mean  ", statistics.mean(lst))
    print(title, "minmax", min(lst), max(lst))


def get_git_message_lengths():
    marker = secrets.token_urlsafe(16)

    messages = get_output(f"git log '--pretty=%B{marker}'").split(marker)

    first_line_lengths = []
    rest_line_lengths = []
    message_line_counts = []
    message_lengths = []

    for message in messages:
        lines = [line for line in (line.strip() for line in message.splitlines()) if line]
        if not lines:
            continue
        message_lengths.append(sum(len(line) for line in lines))
        message_line_counts.append(len(lines))
        first_line_lengths.append(len(lines.pop(0)))
        for line in lines:
            rest_line_lengths.append(len(line))

    return (first_line_lengths, rest_line_lengths, message_line_counts, message_lengths)


@click.command()
def message_stats():
    """
    Print out some statistics about the commit messages in the repo.
    """
    (
        first_line_lengths,
        rest_line_lengths,
        message_line_counts,
        message_lengths,
    ) = get_git_message_lengths()

    print_stats("first line", first_line_lengths)
    print_stats("rest lines", rest_line_lengths)
    print_stats("line count", message_line_counts)
    print_stats("msg length", message_lengths)
