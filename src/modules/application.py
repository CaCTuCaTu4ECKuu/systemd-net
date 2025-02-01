import argparse
from tabulate import tabulate

from modules.core import SVCArgsProp
from modules.NetService import *

SVC_TABLE_HEADERS = ["Name", "URLs", "Enable", "Active"]
def print_services(services:list[NetService]):
    data = []
    if (len(services) > 0):
        for idx,svc in enumerate(services):
            state_enabled = svc.get_service_enabled()
            state_active = svc.get_service_active()
            if state_enabled == 'enabled':
                state_enabled = f"{COLOR_SUCCESS}{state_enabled}{COLOR_BASE}"
            if state_active == 'active':
                state_active = f"{COLOR_SUCCESS}{state_active}{COLOR_BASE}"
            elif state_active == 'failed':
                state_active = f"{COLOR_DANGER}{state_active}{COLOR_BASE}"
            elif state_active == 'activating':
                state_active = f"{COLOR_WARN}{state_active}{COLOR_BASE}"
            urls = svc.ASPNETCORE_URLS.replace(";","\n")

            data.append([svc.Name, urls, state_enabled, state_active])
        print(tabulate(data, headers=SVC_TABLE_HEADERS, tablefmt="grid"))
    else:
        print("No services registered.")

def handle_command(args:argparse.Namespace):
    # List registered services
    if args.command == 'list':
        services = get_services(args.service_dir, args.prefix)
        print_services(services)
        exit()

    # Delete service
    if args.command == 'del':
        svcArgs = SVCArgsProp(args.service_dir, args.prefix, args.service_name)
        if not os.path.isfile(svcArgs.Path):
            print(f"Service not found - {svcArgs.Path}")
            exit(1)

        svc = read_service(svcArgs.Path)
        if svc.get_service_active() == 'active' and not args.force:
            print(f"{COLOR_DANGER}Service is currently active. Use --force to stop and delete service.{COLOR_BASE}")
            exit(1)
        print(f"Deleting service '{svc.Name}' from systemd...")
        delete_service(svcArgs.Path, args.cleanup)
        print(f"{COLOR_SUCCESS}Service '{svc.Name}' deleted from systemd{COLOR_BASE}")
        exit()

    # Register net service
    if args.command == 'add':
        if args.exec_path is None or len(str(args.exec_path).strip()) == 0:
            print(f"{COLOR_DANGER}Service execution path required (-exec){COLOR_BASE}")
            exit(2)

        svcArgs = SVCArgsProp(args.service_dir, args.prefix, args.service_name)
        if os.path.isfile(svcArgs.Path):
            print(f"{COLOR_DANGER}Service already exists - {svcArgs.Path}{COLOR_BASE}")
            exit(1)

        svc = create_service_blank(args.service_dir, svcArgs.Name)
        svc.Params.set_ExecStart(args.exec_path)
        if (args.working_dir and len(args.working_dir) > 0):
            if os.path.isdir(args.working_dir):
                svc.Params.Properties['WorkingDirectory'] = args.working_dir
            else:
                print(f"{COLOR_DANGER}Path is not directory - '{args.working_dir}'{COLOR_BASE}")
                exit(1)
        
        if (args.user and len(args.user) > 0):
            svc.Params.Properties['User'] = args.user
            svc.Params.Properties['Group'] = args.user

        if args.aspnetcore_urls is not None and len(str(args.aspnetcore_urls)) > 0:
            svc.ASPNETCORE_URLS = args.aspnetcore_urls # TODO: autofill defaults
        svc.ASPNETCORE_ENVIRONMENT = args.aspnetcore_env

        svc.try_save(args.service_dir)
        print(f"{COLOR_SUCCESS}Service {svc.Name} added to systemd - {svc.ServicePath}{COLOR_BASE}")
        exit()
    
    if args.command == 'edit':
        app = str(args.app)
        svcArgs = SVCArgsProp(args.service_dir, args.prefix, args.service_name)
        if not os.path.isfile(svcArgs.Path):
            print(f"Service not found - {svcArgs.Path}")
            exit(1)

        if args.env:
            svc = read_service(svcArgs.Path)
            if not os.path.isfile(svc.EnvironmentFile):
                print(f"Environment file not found - {svc.EnvironmentFile}")
                exit(1)
            subprocess.run([app, svc.EnvironmentFile])
            exit()

        subprocess.run([app, svcArgs.Path])
        exit()
    
    if args.command == 'start':
        svcArgs = SVCArgsProp(args.service_dir, args.prefix, args.service_name)
        if not os.path.isfile(svcArgs.Path):
            print(f"Service not found - {svcArgs.Path}")
            exit(1)
        
        svc = read_service(svcArgs.Path)
        svc_state = svc.get_service_active()
        if (svc_state != 'active') and (svc_state != 'activating'):
            subprocess.run(['systemctl', 'start', svcArgs.FullName], text=True, check=True)
        
        exit()
    
    if args.command == 'stop':
        svcArgs = SVCArgsProp(args.service_dir, args.prefix, args.service_name)
        if not os.path.isfile(svcArgs.Path):
            print(f"Service not found - {svcArgs.Path}")
            exit(1)

        svc = read_service(svcArgs.Path)
        svc_state = svc.get_service_active()
        if (svc_state == 'active') or (svc_state == 'activating'):
            subprocess.run(['systemctl', 'stop', svcArgs.FullName], text=True, check=True)
        
        exit()