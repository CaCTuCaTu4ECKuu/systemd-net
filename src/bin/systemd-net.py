#!/usr/bin/env python3

import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.core import *
from modules.NetService import *
from modules.application import *

DOTNET_CLI = "/usr/bin/dotnet"

DOTNET_INSTALLED = is_dotnet_installed(DOTNET_CLI)
RUNTIMES = get_dotnet_runtimes(DOTNET_CLI)
#CURRENT_USER = pwd.getpwuid(os.getuid())[0]

args = app_argsparser.parse_args()
handle_command(args)

def main():
    if not DOTNET_INSTALLED:
        print(f"{COLOR_WARN}Warning: {DOTNET_CLI} not found. Only self-contained apps can run.{COLOR_BASE}")
    print(args)

    #svc = create_service_blank(args.service_dir, 'netapp.test')
    #svc.Description = 'Test Service'
    #svc.Params.Properties['WorkingDirectory'] = '/www/AppDir/'
    #svc.Params.set_ExecStart('/www/AppDir/file.dll')
    #svc.Params.Properties['SyslogIdentifier'] = svc.Name
    #svc.Params.Properties['User'] = CURRENT_USER
    #svc.Params.Properties['Group'] = CURRENT_USER
    #svc.EnvironmentFile = f"{args.env_dir}{svc.Name}.env"
    #svc.ASPNETCORE_URLS = 'http://+:5001'
    #svc.ASPNETCORE_ENVIRONMENT = 'Development'
    #svc.try_save(args.service_dir)

    time.sleep(0.25)
    services = get_services(args.service_dir, args.prefix)
    print_services(services)

if __name__ == "__main__":
    main()