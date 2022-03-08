import logging
import os
import sys
import glob
import requests
from subprocess import Popen, PIPE, TimeoutExpired, run
import platform
import shutil
from logging import info, debug, error, warning
from getpass import getpass
import json

from configs import network_config, usercfg


# logging_level = os.environ.get('LOGGING_LEVEL', logging.INFO)
# logging.basicConfig(format='%(asctime)s-[%(process)d]-%(levelname)s-%(message)s', level=logging_level)


class Linux:
    def __init__(self, ubuntu=True):

        if 'Linux' not in platform.system():
            error(f'OS not Linux. Exiting: {platform.system()}')
            sys.exit(-1)

        # TODO: dictionary input rather than json file

        # NOTE: There is no good way around this. Either write to privlaged files using cli tools, or run as sudo.
        # Must enter password twice
        if os.geteuid() != 0:
            os.execvp('sudo', ['sudo', '-S', 'venv/bin/python'] + sys.argv)

        # Running as root, password not needed
        # self.password = getpass(prompt='Password: ', stream=None)
        self.password = True

        config = self.read_config('configs.json')
        logging_level = config['logging_level']
        # TODO: set logging level in json
        # logging_level = os.environ.get('LOGGING_LEVEL', logging.DEBUG)
        logging.basicConfig(format='%(asctime)s-[%(process)d]-%(levelname)s-%(message)s', level=logging_level)

        # bootstrap dev system
        info('Updating the dev environment and bootstrapping')
        self.shell('apt-get update')
        bootstrap = f"apt-get install -y {config['software']['bootstrap']}"
        debug(f'bootstrap command: {bootstrap}')
        self.shell(bootstrap)

        self.linux = config['linux']
        version = config['version']
        self.url = self.read_config('linux.json')[self.linux][version]
        self.path = config['download_path']
        self.partitions = []
        self.boot_part = ''
        self.root_part = ''
        self.loop = ''
        self.enable_wifi = eval(config['enable_wifi'])
        self.enable_bluetooth = eval(config['enable_bluetooth'])
        self.use_lcd = eval(config['use_lcd'])

        # start manipulating img
        self.download()
        # TODO: fix resize
        # self.resize(400)
        self.losetup()
        self.mount()

        self.update_wifi(config['networks'])
        self.create_users(config['users'])
        self.update_user_cfg()

        # self.unmount()
        # self.cleanup()

    def resize(self, size: int):
        add_size = f'dd if=/dev/zero bs=1M count={size} >> {self.decompressed_path}'
        debug(f'add space command: {add_size}')
        self.shell(add_size)

        get_size = f'parted -s {self.decompressed_path} print free'
        size = self.shell(get_size).split('MB')[-3] + 'MB'
        debug(f'new disk size: {size}')

        resize_command = f'parted -s {self.decompressed_path} resizepart 2 {size}'
        self.shell(resize_command)

    def download(self):
        """
        Download and decompress image.

        :return:
        """
        path = self.path
        if not os.path.isfile(path):
            info(f'Downloading image at {path}')
            file = requests.get(self.url, allow_redirects=True, stream=True)
            total_size = int(file.headers.get('content-length', 0))
            block_size = 1024
            open(path, 'wb').write(file.content)
        else:
            info(f'image already downloaded at {path}')

        if not os.path.isfile(path[:-3]):
            info(f'Decompressing {path}')
            self.shell(f'xz --decompress --keep {path}')
        else:
            info(f'File exists: {path[:-3]}')

        self.decompressed_path = path[:-3]
        info(f'Using file: {self.decompressed_path}')

    def losetup(self):
        path = self.decompressed_path
        command = f'losetup --show -f -P {path}'
        self.loop = self.shell(command)
        info(f'Mounted {path} at {self.loop}')

    def mount(self):
        self.partitions = glob.glob(f'{self.loop}p*')
        debug(f'Partitions: {self.partitions}')

        for p in self.partitions:
            part = p[5:]
            if '1' in part:
                self.boot_part = f'/mnt/{part}'
            elif '2' in part:
                self.root_part = f'/mnt/{part}'
            else:
                error(f'Unhandled partition: {part}')
                sys.exit()

            debug(f'mounting {p} at /mnt/{part}')
            self.shell(f'mkdir -p /mnt/{part}')
            self.shell(f'mount {p} /mnt/{part}')

        self.copy_file(source='/usr/bin/qemu-aarch64-static', destination=f'{self.root_part}/usr/bin')
        self.copy_file(source='/usr/bin/qemu-arm-static', destination=f'{self.root_part}/usr/bin')

    def unmount(self):

        for p in self.partitions:
            debug(f'unmounting {p} at /mnt/{p[5:]}')
            self.shell(f'umount /mnt/{p[5:]}')
        info(f'Unmounting {self.loop}')

    def cleanup(self):
        for p in self.partitions:
            debug(f'removing /mnt/{p[5:]}')
            self.shell(f'rm -r /mnt/{p[5:]}')

        command = f'losetup -d {self.loop}'
        debug(f'command: {command}')
        self.shell(command)
        info(f'Unmounting {self.loop}')

    def update_user_cfg(self):
        """
        update usercfg.txt

        :return: None
        """
        wifi = None
        bluetooth = None
        rotate = None
        lcd = None
        use_lcd = False
        path = f'{self.boot_part}/usercfg.txt'

        if not self.enable_wifi:
            wifi = 'dtoverlay=disable-wifi'
        if not self.enable_bluetooth:
            bluetooth = 'dtoverlay=disable-bt'
        if self.linux == 'ubuntu':
            rotate = 'display_lcd_rotate=2'
        if self.use_lcd:
            lcd = """
            hdmi_group=2
            hdmi_mode=87
            hdmi_timings=480 0 40 10 80 800 0 13 3 32 0 0 0 60 0 32000000 3
            dtoverlay=ads7846,cs=1,penirq=25,penirq_pull=2,speed=50000,keep_vref_on=0,swapxy=0,pmax=255,xohms=150,xmin=200,xmax=3900,ymin=200,ymax=3900
            display_rotate=1
            hdmi_drive=1
            hdmi_force_hotplug=1
            
            """.strip().replace('            ', '')  # This is dumb

        config = '\n'.join(filter(None, [wifi, bluetooth, rotate, lcd]))
        self.append_file(file=path, contents=config)

    def update_wifi(self, networks: list):
        """
        Writes wifi credentials to /boot/firmware/network-config. Dev mount in /mnt/loop{n}p1/network-config
        NOTE: This method overwrites the file every time.

        STRUCTURE:
        networks = [
            {
                'ssid': 'SSID1',
                'password': 'PassWord1'
            },
            {
                'ssid': 'SSID2',
                'password': 'Password2'
            }
        ]

        :param networks: list of dictionaries containing ssid and password for each network
        :type networks: list
        :return: None
        """
        try:
            path = f'{self.boot_part}/network-config'
            os.path.isfile(path)
        except Exception as e:
            error(f'Path exception: {e}')
            sys.exit(-1)
        finally:
            try:
                with open(path, 'w') as f:
                    f.write(network_config)
                    for network in networks:
                        f.write(f'      {network["ssid"]}:\n')
                        f.write(f'        password: "{network["password"]}"\n')
            except Exception as e:
                error(f'Error writing to {path}: {e}')
                sys.exit(-1)

    def copy_file(self, source: str, destination: str):
        try:
            shutil.copy2(source, destination)
        except Exception as e:
            error(f'Error while copying file: {e}')

    def append_file(self, file: str, contents: str):
        try:
            with open(file, 'a+') as f:
                f.write(contents)
        except Exception as e:
            error(f'Error while appending file: {e}')

    # @deprecation.deprecated(deprecated_in='0.1', details='Use shell() instead')
    def shell(self, command: str):
        """
        Runs Linux shell command with or without sudo. Pipes should be avoided. Using sudo will prompt for password.

        Usage:
            shell_command(command='<command>)


        Shell script equivalent:
        echo $password | sudo -S $command

        :param command: shell command
        :type command: str
        :return: command output
        """

        command = command.split(' ')
        try:
            password = self.password
        except Exception as e:
            error(f'password error: {e}')
            sys.exit(-1)

        if 'sudo' in command and '-S' not in command and command[0] == 'sudo':
            command.insert(1, '-S')
        try:
            if 'sudo' in command:
                passwd = Popen(['echo', password], stdout=PIPE)
                if '>>' in command:  # This didn't work correctly
                    index = command.index('>>')
                    output = command[-1]
                    in_cmd = command[:index - 1]
                    debug(f'command has >>: index: {index}, input: {in_cmd} output: {output}')
                    with open(output) as f:
                        shell_cmd = Popen(in_cmd, stdin=passwd.stdout, stderr=f)
                else:
                    shell_cmd = Popen(command, stdin=passwd.stdout, stdout=PIPE)
            else:
                shell_cmd = Popen(command, stdout=PIPE)
        except Exception as e:
            error(f'Error running command {" ".join(command)}: {e}')
            sys.exit(-1)

        out, err = shell_cmd.communicate()

        if err:
            error(err)
        if out:
            debug(f'SHELL COMMAND: {" ".join(command)} OUTPUT: {out}')
            return out.decode('utf-8').replace('\n', '')

    def create_users(self, users: list):
        """
        Read users from a list.

        list format:   "users:": [
                                    {
                                      "user": "ubuntu",
                                      "password": "password",
                                      "admin": "False"
                                    },
                                    {
                                      "user": "iotadmin",
                                      "password": "password",
                                      "admin": "True"
                                    }
                                ],

        :param users: list of dictionaries
        :return: None
        """

        for user in users:
            username = user['user']
            password = user['password']
            admin = eval(user['admin'])
            groups = ["dialout", "docker", "i2c"]

            debug(f'Creating user: {username}, passwd: {password}, admin: {admin}, groups: {groups}')

            try:
                for group in groups:
                    make_group = f'chroot {self.root_part} groupadd -f {group}'
                    self.shell(make_group)

                if admin:
                    groups.append("sudo")

                make_group = f'chroot {self.root_part} groupadd -f {username}'
                # groups.remove(username)
                make_user = f'chroot {self.root_part} useradd -m -s /bin/bash -U -G {",".join(groups)} -p {password} {username}'
                debug(f'make user command: {make_user}')

                # self.shell(make_group)
                self.shell(make_user)

            except Exception as e:
                error(f'Error creating user {username}: {e}')
                sys.exit(-1)

    def proot(self, command: str) -> str:
        """
        Run a command under full emulation as root.

        DO NOT USE sudo


        :param partition:
        :param command:
        :return: proot command
        """

        partition = self.root_part

        if 'sudo' in command:
            cmd = command.split(' ')
            cmd.remove('sudo')
            command = ' '.join(cmd)
        return f'proot -q quemu-aarch64 -w / -b /bin/bash:/bin/sh -S {partition} {command}'
        # return f'sudo proot -q quemu-aarch64 -w / -b /bin/bash:/bin/sh -S {partition} {command}'

    def read_config(self, path: str) -> dict:
        """

        Load configuration from json file.

        :param path: json formatted file path
        :return: None
        """

        if not os.path.exists(path):
            error(f'{path} does not exist')
            sys.exit(-1)

        try:
            with open(path, 'r') as f:
                # TODO: validate json formatting
                return json.load(f)
        except Exception as e:
            error(f'Error reading {path}: {e}')
            sys.exit(-1)

    def validate_config(self, config: dict):
        """
        Validate json from flask API.

        :param config:
        :return:
        """
        pass


if __name__ == '__main__':
    linux = Linux()
