import re

from .command_base import Command


class SaySentenceCommand(Command):
    command_regexp = re.compile(r"^(скажи|расскажи)\s+(.+)", re.IGNORECASE)

    def execute(self) -> str:
        match = self.command_regexp.search(self.text)
        return match.group(2).strip().lower()
