import logging
import os
import subprocess
import sys
from subprocess import Popen, run, PIPE
from logging import info, error, debug, warning
from getpass import getpass

logging_level = os.environ.get('LOGGING_LEVEL', logging.INFO)
logging.basicConfig(format='%(asctime)s-[%(process)d]-%(levelname)s-%(message)s', level=logging_level)


# def shell_command(command:str):
#     cmd = command.split(' ')
#     logging.info(f'Command: {command}')
#     try:
#         output = run(cmd, shell=True, check=True, capture_output=False, stdout=subprocess.PIPE).stdout.decode('utf-8')
#         logging.debug(f'Output: {output}')
#         return output
#     except Exception as e:
#         logging.error(f'An error ocured while running {command} with output: {e}')
#     return output

def shell(command: str):
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
        password = getpass('password: ')
    except Exception as e:
        error(f'password error: {e}')
        sys.exit(-1)

    if 'sudo' in command and '-S' not in command and command[0] == 'sudo':
        command.insert(1, '-S')

    if 'sudo' in command:
        passwd = Popen(['echo', password], stdout=PIPE)
        shell_cmd = Popen(command, stdin=passwd.stdout, stdout=PIPE)
    else:
        shell_cmd = Popen(command, stdout=PIPE)

    out, err = shell_cmd.communicate()

    if err:
        error(err)
    if out:
        info(f'SHELL COMMAND: {" ".join(command)} OUTPUT: {out}')
        return out.decode('utf-8').replace('\n', '')


def main():
    # out = shell_command('ls -l | grep main')
    # logging.info(out)
    # out = shell('ps aux | grep snap')
    path = '/tmp/raspi.img'
    get_size = f'sudo parted -s {path} print free'
    size = shell(get_size).split('MB')[-3] + 'MB'
    print(size)


if __name__ == '__main__':
    main()
