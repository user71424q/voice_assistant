class Command:
    command_description: dict = {}

    @classmethod
    def execute(cls) -> None | str:
        raise NotImplementedError("Команда должна реализовывать метод execute()")
