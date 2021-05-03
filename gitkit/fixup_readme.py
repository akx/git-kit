import io
import re

from .cli import cli


def generate_commands_markdown() -> str:
    sio = io.StringIO()
    print('| Command | Description |', file=sio)
    print('| ------- | ----------- |', file=sio)
    for name, cmd in sorted(cli.commands.items()):
        print(f'| `{name}` | {cmd.help.strip()} |', file=sio)
    return sio.getvalue().strip()


def replace_fragment(source: str, marker: str, value: str) -> str:
    start_marker = f'<!-- start {marker} -->'
    end_marker = f'<!-- end {marker} -->'
    return re.sub(
        rf'{re.escape(start_marker)}(.+?){re.escape(end_marker)}',
        f'{start_marker}\n{value}\n{end_marker}',
        source,
        flags=re.DOTALL,
    )


def main():
    with open("README.md", encoding="UTF-8") as f:
        readme = f.read()

    readme = replace_fragment(readme, "commands", generate_commands_markdown())

    with open("README.md", "w", encoding="UTF-8") as f:
        f.write(readme)


if __name__ == '__main__':
    main()
