import subprocess
from .command_base import Command
import re

class SleepPCCommand(Command):
    command_regexp = re.compile(r'(пк|компьютер|комп) (в спящий|в сон|спать|в спячку)', re.IGNORECASE)
    
    def execute(self) -> None | str:
        try:
            subprocess.run(['powershell', '-Command', 'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState("Suspend", $false, $true)'], check=True)
        except subprocess.CalledProcessError:
            return "Не удалось перевести компьютер в спящий режим"