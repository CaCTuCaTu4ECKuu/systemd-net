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
app_cmdparser = app_argsparser.add_subparsers(dest='command', help='Avaliable commands')

common_parser = argparse.ArgumentParser(add_help=False)
common_parser.add_argument('-p', '--prefix', type=str, help="Prefix to filter services\n(default: '%(default)s')", default="netapp.")

app_addparser = app_cmdparser.add_parser('add', parents=[common_parser], help='Add application')
app_addparser.add_argument('service_name', type=str, help='Name of service in systemd')
app_addparser.add_argument('exec_path', type=str, help="Path to application executable (.dll)")
app_addparser.add_argument('-sdir', '--service-dir', type=str, help=".service files directory\n(default: %(default)s)", default="/etc/systemd/system/")
app_addparser.add_argument('-edir', '--env-dir', type=str, help=".env files directory\n(default: %(default)s)", default="/etc/systemd/system/env/")
app_addparser.add_argument('-wdir', '--working-dir', help="Application working directory\n(default same as 'exec_path' directory)")
app_addparser.add_argument('-u', '--user', help='User to run application\n(default: %(default)s)', default='www-data')
app_addparser.add_argument('--aspnetcore-env', type=str, help="ASPNETCORE_ENVIRONMENT environment variable (default: '%(default)s')", default="Production")
app_addparser.add_argument('--aspnetcore-urls', type=str, help="ASPNETCORE_URLS environment variable", default=None)

app_delparser = app_cmdparser.add_parser('del', parents=[common_parser], help='Delete application')
app_delparser.add_argument('service_name', help='Name of service in systemd (with prefix)')
app_delparser.add_argument('-sdir', '--service-dir', type=str, help=".service files directory\n(default: %(default)s)", default="/etc/systemd/system/")
app_delparser.add_argument('-F', '--force', help="Force deletion", action="store_true")
app_delparser.add_argument('--cleanup', help="Delete service and environment .bak files\n(default is false)", action="store_true", default=False)

app_listparser = app_cmdparser.add_parser('list', parents=[common_parser], help='List registered applications')
app_listparser.add_argument('-sdir', '--service-dir', type=str, help=".service files directory\n(default: %(default)s)", default="/etc/systemd/system/")

app_editparser = app_cmdparser.add_parser('edit', parents=[common_parser], help="Edit with text editor")
app_editparser.add_argument('app', help="Application of your choise to use for edit ('vi', 'nano', etc.)")
app_editparser.add_argument('service_name', help="Name of service in systemd")
app_editparser.add_argument('-sdir', '--service-dir', type=str, help=".service files directory\n(default: %(default)s)", default="/etc/systemd/system/")
app_editparser.add_argument('--env', help="Edit environment file defined in service", action="store_true")

app_startparser = app_cmdparser.add_parser('start', parents=[common_parser], help="Start application")
app_startparser.add_argument('service_name', type=str, help='Name of service in systemd')
app_startparser.add_argument('-sdir', '--service-dir', type=str, help=".service files directory\n(default: %(default)s)", default="/etc/systemd/system/")

app_stopparser = app_cmdparser.add_parser('stop', parents=[common_parser], help="Stop application")
app_stopparser.add_argument('service_name', type=str, help='Name of service in systemd')
app_stopparser.add_argument('-sdir', '--service-dir', type=str, help=".service files directory\n(default: %(default)s)", default="/etc/systemd/system/")

class SVCArgsProp:
    ServiceDir:str
    Prefix:str
    Name:str
    FullName:str
    Path:str
    
    def __init__(self, sdir, prefix, name):
        self.ServiceDir = str(sdir)
        self.Prefix = str(prefix)
        self.Name = str(name)

        if not self.Name.startswith(self.Prefix):
            self.FullName = f"{self.Prefix}{self.Name}"
        else:
            self.FullName = self.Name
            self.Name = self.Name.removeprefix(self.Prefix)
        
        self.Path = os.path.join(self.ServiceDir, self.FullName)
        if not self.Path.endswith('.service'):
            self.Path = f"{self.Path}.service"
        

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