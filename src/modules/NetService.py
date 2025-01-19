import os
from datetime import datetime

from modules.core import *
from modules.services import *

class NetService:
    Name:str = None
    ServicePath:str = None

    Unit:ServiceUnit = ServiceUnit()
    Params:ServiceParameters = ServiceParameters()
    Install:ServiceInstall = ServiceInstall()
    Environment:dict[str, str] = {}

    @property
    def Description(self)->Optional[str]:
        return self.Unit.Description

    @Description.setter
    def Description(self,value:str):
        self.Unit.Description = value

    @property
    def EnvironmentFile(self)->Optional[str]:
        return self.Params.Properties.get('EnvironmentFile', None)

    @EnvironmentFile.setter
    def EnvironmentFile(self, value:str):
        self.Params.Properties['EnvironmentFile'] = value

    @property
    def ExecUser(self):
        return self.Params.Properties.get('User', None)

    @ExecUser.setter
    def ExecUser(self, user:str):
        self.Params.Properties['User'] = user

    @property
    def ExecGroup(self):
        return self.Params.Properties.get('Group', None)

    @ExecGroup.setter
    def ExecGroup(self, group:str):
        self.Params.Properties['Group'] = group

    def get_environment_variable(self, key:str)->Optional[str]:
        if key in self.Environment:
            value = self.Environment[key]
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return value
        return None

    def set_environment_variable(self, key:str, value:str):
        val = value.strip()
        if val.startswith('"') and val.endswith('"'):
            self.Environment[key] = val
        else:
            self.Environment[key] = f"\"{val}\""

    @property
    def ASPNETCORE_URLS(self)->Optional[str]:
        return self.get_environment_variable('ASPNETCORE_URLS')

    @ASPNETCORE_URLS.setter
    def ASPNETCORE_URLS(self, value:str):
        self.set_environment_variable('ASPNETCORE_URLS', value)

    @property
    def ASPNETCORE_ENVIRONMENT(self)->Optional[str]:
        return self.get_environment_variable('ASPNETCORE_ENVIRONMENT')

    @ASPNETCORE_ENVIRONMENT.setter
    def ASPNETCORE_ENVIRONMENT(self, value:str):
        self.set_environment_variable('ASPNETCORE_ENVIRONMENT', value)

    def __write_file(self, file_path:str, chmod=0o644):
        lines = [
            TOOL_FILEGEN_COMMENT,
            f"# {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", '',
            self.Unit.format_section(), '',
            self.Params.format_section(), '',
            self.Install.format_section()
        ]

        with open(file_path, 'w') as file:
            file.write('\n'.join(lines))
        os.chmod(file_path, chmod)
    
    def __write_env(self, file_path:str, chmod=0o644):
        lines = [ TOOL_FILEGEN_COMMENT, f"# {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}" ]
        for key,value in self.Environment.items():
            lines.append(f"{key}={value}")

        with open(file_path, 'w') as file:
            file.write('\n'.join(lines))
        os.chmod(file_path, chmod)

    def try_save(self, svc_dir:str, rewrite=True, chmod=0o644):
        save_fpath = os.path.join(svc_dir, f"{self.Name}.service")
        env_fpath = self.EnvironmentFile
        if env_fpath is None or len(env_fpath.strip()) == 0:
            env_fpath = os.path.join(svc_dir, f"{self.Name}.env")
        self.EnvironmentFile = env_fpath # ensure env file path before save

        rename_svc = False
        rename_env = False
        if os.path.isfile(save_fpath):
            if (rewrite is False):
                print(f"{COLOR_DANGER}Error: file {save_fpath} exists and rewrite is disabled.{COLOR_BASE}")
                return False
            rename_svc = True

        if os.path.isfile(env_fpath):
            if (rewrite is False):
                print(f"{COLOR_DANGER}Error: file {env_fpath} exists and rewrite is disabled.{COLOR_BASE}")
                return False
            rename_env = True

        if rename_svc:
            os.rename(save_fpath, f"{save_fpath}.bak")
        if rename_env:
            os.rename(env_fpath, f"{env_fpath}.bak")

        self.__write_file(save_fpath, chmod)
        self.ServicePath = save_fpath
        self.__write_env(env_fpath, chmod)
        return True

    def get_service_enabled(self):
        result = subprocess.run(
            ["systemctl", "is-enabled", self.Name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout.strip()

    def get_service_active(self):
        result = subprocess.run(
            ["systemctl", "is-active", self.Name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout.strip()

def __read_file(file_path:str):
    sections:dict[str,dict[str,str]] = {}
    current_section:str = None
    current_dict:dict[str,str] = {}
    with open(file_path, 'r') as file:
        for line in file:
            if not line:
                continue
            line = line.strip()

            if line.startswith('[') and line.endswith(']'):
                if current_section is not None:
                    sections[current_section] = current_dict

                current_section = line[1:-1]
                current_dict = {}
            else:
                if '=' in line:
                    key, value = line.split('=', 1)
                    current_dict[key.strip()] = value.strip()

        if current_section is not None:
            sections[current_section] = current_dict
    return sections

def __read_env(file_path:str):
    env:dict[str,str] = {}
    with open(file_path, 'r') as file:
        for line in file:
            if not line:
                continue
            line = line.strip()
            if line.startswith('#'):
                continue # skip comments

            if '=' in line:
                key, value = line.split('=', 1)
                env[key.strip()] = value.strip()
    return env

def read_service(svc_path:str)->NetService:
    if not os.path.isfile(svc_path):
        raise Exception(f"File not found - {svc_path}")
    if not svc_path.endswith('.service'):
        raise Exception(f"{svc_path} is not a service")

    svc_name = os.path.basename(svc_path)[0:-8]

    svc_data = __read_file(svc_path)
    if not 'Service' in svc_data or not 'Unit' in svc_data:
        raise Exception(f"Cannot read {svc_path} - invalid type of service or missing description")

    svc = NetService()
    svc.Name = svc_name
    svc.ServicePath = svc_path

    for prop, value in svc_data['Unit'].items():
        svc.Unit.Properties[prop] = value
    for prop, value in svc_data['Service'].items():
        svc.Params.Properties[prop] = value
    for prop, value in svc_data['Install'].items():
        svc.Install.Properties[prop] = value
    if svc.EnvironmentFile is not None:
        if os.path.isfile(svc.EnvironmentFile):
            svc.Environment = __read_env(svc.EnvironmentFile)
        else:
            print(f"{COLOR_WARN}Missing EnvironmentFile {svc.EnvironmentFile}{COLOR_BASE}")
    return svc

def get_services(services_dir:str, prefix:str):
    service_files = list_service_files(services_dir, prefix)
    services:list[NetService] = []
    for service_path in service_files:
        try:
            services.append(read_service(service_path))
        except:
            print(f"{COLOR_WARN}Unable to read service {service_path}{COLOR_BASE}")
    return services

def create_service_blank(svc_dir:str, name:str):
    svc_name = name.strip()
    if not svc_name.endswith('.service'):
        svc_name = f"{svc_name}.service"
    svc_path = os.path.join(svc_dir, svc_name)

    if (os.path.isfile(svc_path)):
        print(f"{COLOR_DANGER}Error: service at {svc_path} already exists.{COLOR_BASE}")
        return None

    svc = NetService()
    svc.Name = svc_name[0:-8]
    svc.ServicePath = svc_path
    svc.Params.Properties['SyslogIdentifier'] = svc.Name
    svc.EnvironmentFile = os.path.join(svc_dir, f"{svc.Name}.env")

    return svc

def delete_service(svc_path:str, clear_bak=False):
    if not os.path.isfile(svc_path):
        return True
    if not svc_path.endswith('.service'):
        print(f"{COLOR_DANGER}Error: {svc_path} is not service.{COLOR_BASE}")
        return False

    svc = read_service(svc_path)
    do_disable_service(svc.Name)

    svc_env_file = svc.EnvironmentFile
    if svc_env_file is not None:
        if clear_bak and (os.path.isfile(f"{svc_env_file}.bak")):
            os.remove(f"{svc_env_file}.bak")
        if (os.path.isfile(svc_env_file)):
            os.remove(svc_env_file)
    
    if clear_bak:
        if (os.path.isfile(f"{svc_path}.bak")):
            os.remove(f"{svc_path}.bak")
    os.remove(svc_path)

    do_reload_systemctl()
    return True