import os
from typing import Optional
from modules.core import *

class ServiceSection:
    Name:str = None
    Properties:dict[str,str] = {}

    def __init__(self, name:str):
        if (len(name.strip()) == 0):
            raise Exception(f"Invalid section name '{name}'")
        self.Name = name

    def format_section(self)->str:
        lines:list[str] = [f"[{self.Name}]"]
        for key, val in self.Properties.items():
            lines.append(f"{key}={val}")
        return '\n'.join(lines)

class ServiceUnit(ServiceSection):
    def __init__(self):
        super().__init__('Unit')
        # Default properties for [Unit] section
        self.Properties = {
            'Description': '.NET Application'
        }

    @property
    def Description(self)->Optional[str]:
        return self.Properties.get('Description', None)

    @Description.setter
    def Description(self, value:str):
        self.Properties['Description'] = value

class ServiceParameters(ServiceSection):
    def __init__(self):
        super().__init__('Service')
        # Default properties for [Service] section
        self.Properties = {
            'WorkingDirectory': '',
            'ExecStart': '',
            'Restart': 'always',
            'RestartSec': '5',
            'KillSignal': 'SIGINT',
            'User': 'www-data',
            'Group': 'www-data'
        }
    
    def set_ExecStart(self, path:str, dotnet:str="/usr/bin/dotnet", ensure_app=False):
        if ensure_app and not os.path.isfile(path):
            raise Exception('Missing file {path}')
        if dotnet is not None and len(dotnet) > 0:
            self.Properties['ExecStart'] = f"{dotnet} {path}"
        else:
            self.Properties['ExecStart'] = path

        wdir = self.Properties.get('WorkingDirectory', '')
        if len(wdir.strip()) == 0:
            self.Properties['WorkingDirectory'] = os.path.dirname(path)
        elif not path.startswith(wdir):
            print(f"{COLOR_WARN}Execution path is not in the working directory{COLOR_BASE}")

class ServiceInstall(ServiceSection):
    def __init__(self):
        super().__init__('Install')
        # Default [Install] section
        self.Properties = {
            'WantedBy': 'multi-user.target'
        }

    def format_section(self)->str:
        lines:list[str] = [f"[{self.Name}]"]

        if ('WantedBy' in self.Properties):
            lines.append(f"WantedBy={self.Properties['WantedBy']}")
        if ('RequiredBy' in self.Properties):
            lines.append(f"RequiredBy={self.Properties['RequiredBy']}")
        if ('Also' in self.Properties):
            lines.append(f"Also={self.Properties['Also']}")
        if ('Alias' in self.Properties):
            lines.append(f"Alias={self.Properties['Alias']}")

        return '\n'.join(lines)
