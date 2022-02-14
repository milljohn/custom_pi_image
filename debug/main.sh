#!/bin/bash

. colors.sh # ansi colors in the terminal
# colors setup
initializeANSI

. los.sh # mount and unmount multiple partitions on an image
los "/tmp/raspi.img"

# n is in los

bootPart="/mnt/loop${n}p1"
linuxPart="/mnt/loop${n}p2"


get_shell(){
    PARTITION=$1
    printf "${yellowf}Full shell with root at $PARITION${reset}\n"

    sudo proot -q qemu-aarch64 -w / -b /bin/bash:/bin/sh -S $PARTITION

    printf "${yellowf}Shell closed at $PARITION${reset}\n"
}

proot_command(){
    command=$1
    sudo proot -q qemu-aarch64 -w / -b /bin/bash:/bin/sh -S $linuxPart $command
}

 printf "${yellowf}Chrooting into fs. Make any final changes. Type 'exit' to continue:${reset}\n"
 printf "${yellowf}NOTE: You currnetly cannot use the network, e.g apt, curl, wget. Use the network post-installation.${reset}\n"
 sudo chroot $linuxPart

#printf "${yellowf}prooting into fs. Make any final changes. Type 'exit' to continue:${reset}\n"
#printf "${yellowf}NOTE: You may use the network, e.g apt, curl, wget. There may be some unstability with apt-get upgrade.${reset}\n"
#get_shell $linuxPart

## Cleanup
printf "${yellowf}Cleaning up...${reset}\n"
losd $n
printf "${yellowf}Completed. You may now burn the image.${reset}\n"