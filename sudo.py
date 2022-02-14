import logging
import os
import sys
from subprocess import Popen, PIPE, TimeoutExpired

logging_level = os.environ.get('LOGGING_LEVEL', logging.INFO)
logging.basicConfig(format='%(asctime)s-[%(process)d]-%(levelname)s-%(message)s', level=logging_level)

apple = 1

def main():
    if os.geteuid() != 0:
        # passwd = Popen(['echo', 'zenity', '--password'], stdout=PIPE)
        # os.execvp('sudo', ['sudo', '-S', 'python3'] + sys.argv)
        logging.info(sys.argv)
        # os.execvp('sudo', ['sudo', '-A', 'python3'] + sys.argv)
        os.execvp('sudo', ['sudo', '-S', 'python3'] + sys.argv)
    logging.debug('test')
    STDOUT = 1

    fdout = os.open('output.txt', os.O_WRONLY)
    os.dup2(fdout, STDOUT)
    os.execvp('ps', 'ps -a -u -x'.split())
    # not reached
    os._exit(127)  # just for the case of execv failure


if __name__ == '__main__':
    main()
