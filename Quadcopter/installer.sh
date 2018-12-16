#!/bin/bash
while true
do
    echo Before we proceed with the installation, Checking internet connectivity...
    wget -q --spider https://google.com
    if [ $? -eq 0 ]; then
        echo Connected
        #sudo apt-get update 
        #sudo apt-get upgrade
        echo -------------------------------------------------------------
        echo Enabling SSH
        sudo systemctl enable ssh 
        echo SSH enabled
        
        echo -------------------------------------------------------------
        echo Installing Python libraries
        pip install pyserial
        pip install dronekit 
        sudo apt-get install libxml2-dev libxslt-dev 
        sudo apt-get install libjpeg8-dev
        pip install MAVProxy
        pip install luma.core
        pip install luma.oled 
        pip install Pillow
        sudo apt-get install python-dev python-opencv python-wxgtk3.0 python-matplotlib python-pygame python-lxml python-yaml
        sudo apt-get install screen 
        echo Python libraries downloaded 
        
        echo -------------------------------------------------------------
        echo Installing node.js
        cd
        sudo apt-get update
        sudo apt-get dist-upgrade
        wget http://nodejs.org/dist/v0.10.28/node-v0.10.28-linux-arm-pi.tar.gz
        cd /usr/local
        sudo tar -xzf ~/node-v0.10.28-linux-arm-pi.tar.gz --strip=1
        export NODE_PATH=”/usr/local/lib/node_modules”
        echo Testing node with -v
        node -v
        echo Installing Cloud9 IDE
        cd
        git clone git://github.com/c9/core.git c9sdk
        cd c9sdk
        scripts/install-sdk.sh
        
        echo -------------------------------------------------------------
        echo Setting up interfaces...
        cd
        sudo sed -i '$s/$/\nenable_uart=1/' /boot/config.txt
        sudo sed -i 's/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/' /boot/config.txt
        sudo sed -i 's/console=serial0,115200//g' /boot/cmdline.txt
        echo i2c and serial port enabled. 
        
        echo -------------------------------------------------------------
        echo Cloning RCBenchmark repositories and changing working directory.
        cd
        cd Transport_Protocol
        sudo git checkout Transport_Protocol-V2
        sudo git pull

        echo -------------------------------------------------------------
        echo Creating auto launching scripts
        cd
        mkdir autolaunch_scripts
        cd
        (crontab -l ; echo "@reboot screen -d -m -L /home/pi/autolaunch_scripts/mavproxy.log sh /home/pi/autolaunch_scripts/launch_mavproxy_rcb.sh") | sort - | uniq - | crontab -
        sleep 0.1
        (crontab -l ; echo "@reboot screen -d -m -L /home/pi/autolaunch_scripts/pose.log sh /home/pi/autolaunch_scripts/launch_pose_forward_rcb.sh") | sort - | uniq - | crontab -
        sleep 0.1
        (crontab -l ; echo "@reboot screen -d -m -L sh /home/pi/autolaunch_scripts/launch_OLED_screen.sh") | sort - | uniq - | crontab -
        sleep 0.1
        (crontab -l ; echo "@reboot screen -d -m -L sh /home/pi/autolaunch_scripts/launch_c9.sh") | sort - | uniq - | crontab -
        echo Setting up autolaunch_scripts folder
        sudo cp Transport_Protocol/Quad_Environment/launch_mavproxy_rcb.sh /home/pi/autolaunch_scripts
        sudo cp Transport_Protocol/Quad_Environment/launch_pose_forward_rcb.sh /home/pi/autolaunch_scripts
        sudo cp Transport_Protocol/Quad_Environment/launch_OLED_screen.sh /home/pi/autolaunch_scripts
        sudo cp Transport_Protocol/Quad_Environment/launch_c9.sh /home/pi/autolaunch_scripts
        echo Setup Complete! 
        sleep 0.2
        echo -------------------------------------------------------------
        echo Making Files executable
        sudo chmod +x ~/autolaunch_scripts/launch_mavproxy_rcb.sh
        sudo chmod +x ~/autolaunch_scripts/launch_pose_forward_rcb.sh
        sudo chmod +x ~/autolaunch_scripts/launch_OLED_screen.sh
        sudo chmod +x ~/autolaunch_scripts/launch_c9.sh
        echo Creating log deleting scripts
        #sudo sed -i '$i \rm ~/Desktop/pose.log' /etc/r.local
        #sudo sed -i '$i \rm ~/Desktop/mavproxy.log' /etc/rc.local
        echo -------------------------------------------------------------
        echo Cloning and Installing DronecodeSDK
        cd && git clone https://github.com/dronecode/DronecodeSDK.git
        sed -i '\|with vision system|,/}/ s|^|//|'  DronecodeSDK/plugins/action/action_impl.cpp
        cd DronecodeSDK
        git submodule update --init --recursive
        make default 
        sudo make default install
        sudo ldconfig && cd 
        echo Dronecode cloned and installed.
        echo -------------------------------------------------------------
        echo Installing Cmake
        sudo apt-get install cmake 
        echo -------------------------------------------------------------
        echo All dependencies installed
        echo Preparing to reboot 
        echo you have 5 seconds to cancel. to cancel press Ctl+C
        sleep 5
        echo rebooting... 
        sleep 1
        sudo reboot 
        break
    else 
        echo Please connect to wifi and run the script.
    fi
done
