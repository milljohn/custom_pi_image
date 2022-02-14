import logging
import os
from configs import wifi

logging_level = os.environ.get('LOGGING_LEVEL', logging.INFO)
logging.basicConfig(format='%(asctime)s-[%(process)d]-%(levelname)s-%(message)s', level=logging_level)


def main():
    ssid = 'ssid'
    password = 'password'

    networks = [
        {
            'ssid': 'Hedwig',
            'password': 'Hell0Kitty'
        },
        {
            'ssid': 'Innovate',
            'password': 'SwimUpStream'
        }
    ]

    with open("network-config", 'w') as f:
        f.write(wifi)
        for network in networks:
            f.write(f'      {network["ssid"]}:\n')
            f.write(f'        password: "{network["password"]}"\n')

        # txt = f.read()
        # b = """
        # #wifis:
        # #  wlan0:
        # #    dhcp4: true
        # #    optional: true
        # #    access-points:
        # #      myhomewifi:
        # #        password: "S3kr1t"
        # """
        # # config = [ "wifis", "wlan0", "dhcp4", "optional", "access-points", "myhomewifi", "password"]
        # # if any(element in txt for element in config):
        #
        #
        # lines = txt.split('\n')
        # # logging.info(lines)
        # for line in lines:
        #     # logging.info(line)
        #     if 'wifis:' in line:
        #         # logging.info(line)
        #         line = line.replace('#', '')
        #         # print(type(line))
        #         logging.info(line)
        #
        # txt = '\n'.join(lines)
        # f.write(b)
        # print(txt)



if __name__ == '__main__':
    main()
