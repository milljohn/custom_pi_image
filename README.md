# Custom Raspberry Pi Image Creator
This downloads an image for a Raspberry Pi and makes a custom image that can be flashed to an SD card. 


Tested on Ubuntu 20.04  

## Current Version
Reads from configs.json and configs.py

configs.json contains most user variables.

configs.py contains system configuration, such as usercfg.txt and netconfig.

## Future Revisions

1. Make linux_utility take a dictionary input
2. Make a flask API
3. Make a React frontend, possibly electron
4. Package as portable executable