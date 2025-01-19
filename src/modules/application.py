import argparse

from modules.NetService import *

def print_services(services:list[NetService]):
    if (len(services) > 0):
        for idx,svc in enumerate(services):
            print(f"{svc.Name}; {svc.ASPNETCORE_URLS}; {svc.get_service_enabled()}; {svc.get_service_active()}")
    else:
        print("No services registered.")

def handle_command(args:argparse.Namespace):
    # List registered services
    if args.list:
        services = get_services(args.service_dir, args.prefix)
        print_services(services)
        exit(1)

    # Delete service
    if args.delete:
        svc_name = str(args.service_name)
        if not svc_name.startswith(args.prefix):
            svc_name = f"{args.prefix}{svc_name}"

        svc_path = os.path.join(args.service_dir, svc_name)
        if not svc_path.endswith('.service'):
            svc_path = f"{svc_path}.service"
        if not os.path.isfile(svc_path):
            print(f"Service not found - {svc_path}")
            exit(1)
        svc = read_service(svc_path)
        if svc.get_service_active() == 'active' and not args.force:
            print(f"{COLOR_DANGER}Service is currently active. Use --force to stop and delete service.{COLOR_BASE}")
            exit(1)
        print(f"{COLOR_SUCCESS}Service '{svc.Name}' deleted from systemd{COLOR_BASE}")
        delete_service(svc_path)
        exit(1)

    # Register net service
    if args.add:
        svc_name = str(args.service_name)
        if not svc_name.startswith(args.prefix):
            svc_name = f"{args.prefix}{svc_name}"

        svc_path = os.path.join(args.service_dir, svc_name)
        if not svc_path.endswith('.service'):
            svc_path = f"{svc_path}.service"
        if os.path.isfile(svc_path):
            print(f"{COLOR_DANGER}Service already exists - {svc_path}{COLOR_BASE}")
            exit(1)
        if args.exec_path is None or len(str(args.exec_path).strip()) == 0:
            print(f"{COLOR_DANGER}Service execution path required (-exec){COLOR_BASE}")
            exit(1)

        svc = create_service_blank(args.service_dir, svc_name)
        svc.Params.set_ExecStart(args.exec_path)

        if args.aspnetcore_urls is not None and len(str(args.aspnetcore_urls)) > 0:
            svc.ASPNETCORE_URLS = args.aspnetcore_urls # TODO: autofill defaults
        svc.ASPNETCORE_ENVIRONMENT = args.aspnetcore_env

        svc.try_save(args.service_dir)
        print(f"{COLOR_SUCCESS}Service {svc.Name} added to systemd - {svc.ServicePath}{COLOR_BASE}")
        exit(1)