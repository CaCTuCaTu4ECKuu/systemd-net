# systemd-net [UNDER DEVELOPMENT]
This is a tool to simpify and speed up managment of .NET Applications services for systemd

After deploying your application to server just run this tool to create systemd service file and start daemon using `systemctl`

<b>Interactive CLI configurator is under development</b>

## Installation
```bash
git clone https://github.com/CaCTuCaTu4ECKuu/systemd-net
cd systemd-net/src/bin
chmod +x ./systemd-net.py
sudo python3 -m pip install tabulate
```

## Usage
Check `--help` to see avaliable parameters
```bash
./systemd-net.py -h
```
### Create service
```bash
sudo ./systemd-net.py add service_name /www/App/AppName.dll --aspnetcore-urls http://+:5000

sudo systemctl enable netapp.service_name
sudo systemctl start netapp.service_name
```
### List registered services
```bash
./systemd-net.py list
```
### Delete service
```bash
sudo ./systemd-net.py del service_name
```
