#!/bin/bash
while true  # Part 1 of the script
do
    echo Checking internet connectivity before proceeding with the installation:
    wget -q --spider https://google.com
    if [ $? -eq 0 ]; then
	cd
	declare -i err
	err=0
        echo Connected
        #sudo apt-get update 
        #sudo apt-get upgrade
        echo Installer [Part 1/Part 2]
        echo This installer script will install all the necessary tools and dependencies. 
        echo -------------------------------------------------------------
        echo Enabling SSH
        sudo systemctl enable ssh 
        err=err+$?
	echo SSH enabled
	echo -------------------------------------------------------------
    echo Setting up interfaces...
    cd
    sudo sed -i '$s/$/\nenable_uart=1/' /boot/config.txt
    err=err+$?
	sudo sed -i 's/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/' /boot/config.txt
    err=err+$?
	sudo sed -i 's/console=serial0,115200//g' /boot/cmdline.txt
    err=err+$?
	echo i2c and serial port enabled. 
	echo -------------------------------------------------------------
    echo Installing Python libraries
    pip install pyserial
    err=err+$?
	pip install dronekit 
        err=err+$?
    echo "The following libraries will take a upto 20 mins to complete installation."
    echo ------------------------------------------------------------- 
	sudo apt-get -y install libxml2-dev libxslt-dev 
        err=err+$?
    sudo apt-get -y install libjpeg8-dev
        err=err+$?
	# pip install MAVProxy
    #     err=err+$?
	pip install Pillow
        err=err+$?
	pip install luma.oled 
         err=err+$?
	pip install luma.core
        err=err+$?
    sudo apt-get -y install python-dev python-opencv python-wxgtk3.0 python-matplotlib python-pygame python-lxml python-yaml
        err=err+$?
	sudo apt-get -y install screen 
     err=err+$?
	echo Python dependencies downloaded 
    echo Installing MavLink Router.
    cd 
    git clone https://github.com/intel/mavlink-router.git
    cd mavlink-router
    err=err+$?
    git submodule update --init --recursive
    err=err+$?
    sudo apt-get install autoconf automake pkg-config libgtk-3-dev
    err=err+$?
    ./autogen.sh && ./configure CFLAGS='-g -O2' \
        --sysconfdir=/etc --localstatedir=/var --libdir=/usr/lib64 \
    --prefix=/usr
    err=err+$?
    make
    err=err+$?
    make install
	if [ $err -gt 0 ];
	then
	echo Error with MavRouter installation or SSH installation.
	break
	fi
    echo -------------------------------------------------------------
    echo Installing node.js
    cd
    sudo apt-get -y update
    err=err+$?
	sudo apt-get -y dist-upgrade
    err=err+$?
	wget http://nodejs.org/dist/v0.10.28/node-v0.10.28-linux-arm-pi.tar.gz
    err=err+$?
	cd /usr/local
    sudo tar -xzf ~/node-v0.10.28-linux-arm-pi.tar.gz --strip=1
    err=err+$?
	export NODE_PATH=”/usr/local/lib/node_modules”
    echo Testing node with -v
    err=err+$?
	node -v
    echo Installing Cloud9 IDE
    cd
    git clone git://github.com/c9/core.git c9sdk
    cd c9sdk
    scripts/install-sdk.sh
    err=err+$?
    if [ $err -gt 0 ];
	then
	echo Error installing NodeJS or Cloud9
	break
	fi
    while true; do
    read -p $'Do you wish to continue with the second part of the installation \n Enter Y/y for yes or N/n for No: ' yn
    case $yn in
        [Yy]* ) bash /home/pi/Transport_Protocol/Quad_Environment/installer_part2.sh; 
	echo "Part 2/ Part 2 complete. Complete environment Setup on:  $(date)" > /home/pi/Created_on.txt
	echo Part 2/Part 2 complete. Complete Environment is now set up. Details logged in Created_on.txt
	break;;
        [Nn]* ) echo "Part 1/Part 2 installed on: $(date)" > /home/pi/Created_on.txt;	
	echo "Part 1/Part 2 completed."
	exit;;
        * ) echo "Please answer yes or no.";;
    esac
    done
    echo --------------------------------------------------------------
    break
    else 
        echo Please connect to wifi and run the script.
    fi
done
