from typing import Pattern


class Command:

    command_regexp: Pattern[str] = ""

    def __init__(self, text: str):
        self.text = text
        if self.command_regexp == "":
            raise NotImplementedError("Не реализовано регулярное выражение команды")

    def execute(self) -> None | str:
        raise NotImplementedError("Команда должна реализовывать метод execute()")
