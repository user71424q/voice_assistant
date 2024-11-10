import subprocess

from commands.command_base import Command


class SleepPCCommand(Command):
    command_description: dict = {
        "type": "function",
        "function": {
            "name": "SleepPCCommand",
            "description": "Переводит компьютер в спящий режим. Пользователь может сказать, например, 'переведи компьютер в спящий режим'.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    }

    @classmethod
    def execute(cls) -> None | str:
        try:
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState("Suspend", $false, $true)',
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            return "Не удалось перевести компьютер в спящий режим"
