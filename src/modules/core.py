import os
import glob
import subprocess
import argparse

COLOR_BASE = '\033[0m'
COLOR_INFO = '\033[94m'     # BLUE
COLOR_SUCCESS = '\033[92m'  # GREEN
COLOR_WARN = '\033[93m'     # YELLOW
COLOR_DANGER = '\033[91m'   # RED

TOOL_FILEGEN_COMMENT = "# This file was automatically created using systemd-net utility"

app_argsparser = argparse.ArgumentParser(prog='systemd-net', description=f"{COLOR_INFO}systemd-net is utility to easy manage your .NET Applications services{COLOR_BASE}")
app_argsparser.add_argument('-s', '--service-dir', type=str, help="", default="/etc/systemd/system/")
app_argsparser.add_argument('-e', '--env-dir', type=str, help="", default="/etc/systemd/system/env/")
app_argsparser.add_argument('-p', '--prefix', type=str, help="Prefix to filter services", default="netapp.")
app_argsparser.add_argument('-F', '--force', help="Force actoin", action="store_true")
app_argsparser.add_argument('-L', '--list', help="List of registered applications", action="store_true")
app_argsparser.add_argument('-D', '--delete', help="Delete registered service from systemd", action="store_true")
app_argsparser.add_argument('-A', '--add', help="Register new service", action='store_true')
app_argsparser.add_argument('-svc', '--service-name', help="Name of service to do action", default=None)
app_argsparser.add_argument('-exec', '--exec-path', type=str, help="Path to application executable (.dll)", default=None)
app_argsparser.add_argument('--aspnetcore-urls', type=str, help="ASPNETCORE_URLS environment variable", default=None)
app_argsparser.add_argument('--aspnetcore-env', type=str, help="ASPNETCORE_ENVIRONMENT environment variable", default="Production")

def is_dotnet_installed(dotnet_cli_path:str=None):
    if dotnet_cli_path is not None:
        return os.path.exists(dotnet_cli_path)
    return False

def get_dotnet_runtimes(dotnet_cli_path:str):
    if is_dotnet_installed(dotnet_cli_path) == 0:
        return [('Self-contained Deployment', '')]

    result = subprocess.run([dotnet_cli_path, '--list-runtimes'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout.strip()

    runtimes_list:list[tuple[str,str]] = []
    runtimes_list.append(('Self-contained Deployment', ''))

    for line in output.splitlines():
        index = line.find('[')
        if index != -1:
            runtime = line[:index].strip()
            path = line[index+1:-1].strip()

            runtimes_list.append((runtime, path))

    return runtimes_list

def list_dotnet_runtimes(runtimes:list[tuple[str, str]]):
    for idx, (runtime, path) in enumerate(runtimes):
        print(f"{idx}: {runtime}")

def list_service_files(services_dir:str, prefix:str):
    service_files = glob.glob(os.path.join(services_dir, f'{prefix}*.service'))
    return service_files

def do_reload_systemctl():
    subprocess.run(["systemctl", "daemon-reload"])

def do_enable_service(service_name:str):
    subprocess.run(["systemctl", "enable", service_name])

def do_disable_service(service_name:str):
    subprocess.run(["systemctl", "disable", service_name])

def do_start_service(service_name:str):
    subprocess.run(["systemctl", "start", service_name])

def do_stop_service(service_name:str):
    subprocess.run(["systemctl", "stop", service_name])