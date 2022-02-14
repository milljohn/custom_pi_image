#!/bin/bash
# https://askubuntu.com/questions/69363/mount-single-partition-from-image-of-entire-disk-device/673257#673257

# n=0

los() {
  img="$1"
  dev="$(sudo losetup --show -f -P "$img")"
  n=`echo $dev | sed 's/\/dev\/loop//'`
  printf "${yellowf}$dev${reset}\n"
  for part in "$dev"?*; do
    if [ "$part" = "${dev}p*" ]; then
      part="${dev}"
    fi
    dst="/mnt/$(basename "$part")"
    printf "${yellowf}$dst${reset}\n"
    sudo mkdir -p "$dst"
    sudo mount "$part" "$dst"
  done
}
losd() {
  dev="/dev/loop$1"
  for part in "$dev"?*; do
    if [ "$part" = "${dev}p*" ]; then
      part="${dev}"
    fi
    dst="/mnt/$(basename "$part")"
    sudo umount "$dst"
    sudo rm -r $dst
  done
  sudo losetup -d "$dev"
}

# loopNum(){
#     filePath="$1"
#     num=$(losetup -l | grep -v deleted | grep $filePath | awk -F" " '{ print $1 }' | sed 's/\/dev\/loop//')
# }