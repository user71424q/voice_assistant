from .command_base import Command
import re

class SaySentenceCommand(Command):
    command_regexp = re.compile(r'(скажи|расскажи)\s+(.+)', re.IGNORECASE)
    def execute(self) -> str:
       return ' '.join(self.text.split()[1:])
