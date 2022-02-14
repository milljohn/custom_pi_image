



network_config = """
# This file contains a netplan-compatible configuration which cloud-init
# will apply on first-boot. Please refer to the cloud-init documentation and
# the netplan reference for full details:
#
# https://cloudinit.readthedocs.io/
# https://netplan.io/reference
#
# Some additional examples are commented out below

version: 2
ethernets:
  eth0:
    dhcp4: true
    optional: true
wifis:
  wlan0:
    dhcp4: true
    optional: true
    access-points:
"""

usercfg = """
# 4 inch LCD 800x480 settings --- NOTE: Touch is disabled as it doesn't seem to work right anyway.
# edit sysconfig.txt and usercfg.txt in Ubuntu
# edit config.txt in Raspbian

# uncomment for 4-inch LCD
#hdmi_group=2
#hdmi_mode=87
#hdmi_timings=480 0 40 10 80 800 0 13 3 32 0 0 0 60 0 32000000 3
#dtoverlay=ads7846,cs=1,penirq=25,penirq_pull=2,speed=50000,keep_vref_on=0,swapxy=0,pmax=255,xohms=150,xmin=200,xmax=3900,ymin=200,ymax=3900
#display_rotate=1
#hdmi_drive=1
#hdmi_force_hotplug=1

# rotate display for official Raspberry Pi LCD, only necessary with Ubuntu
display_lcd_rotate=2

# disable wifi and bluetooth
#dtoverlay=disable-wifi
#dtoverlay=disable-bt
"""

