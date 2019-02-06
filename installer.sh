#!/bin/bash
cd
        sudo chmod +x ~/autolaunch_scripts/launch_mavproxy_rcb.sh
        err=err+$?
	sudo chmod +x ~/autolaunch_scripts/launch_pose_forward_rcb.sh
        sudo chmod +x ~/autolaunch_scripts/launch_OLED_screen.sh
        err=err+$?
	sudo chmod +x ~/autolaunch_scripts/launch_c9.sh
        err=err+$?
	echo Creating log deleting scripts
        sudo sed -i '$i \rm ~/autolaunch_scripts/pose.log' /etc/rc.local
        err=err+$?
	sudo sed -i '$i \rm ~/autolaunch_scripts/mavproxy.log' /etc/rc.local
        cd && sudo apt-get -y install curl
	sudo apt-get -y install libcurl4-openssl-dev

echo ----------------------------------------------------------------
        echo Cloning and Installing DronecodeSDK
        cd && git clone https://github.com/dronecode/DronecodeSDK.git
        sed -i '\|with vision system|,/}/ s|^|//|'  DronecodeSDK/plugins/action/action_impl.cpp
        err=err+$?
	cd DronecodeSDK
        err=err+$?
	git submodule update --init --recursive
        err=err+$?
	make default 
      	err=err+$?
	sudo make default install
        err=err+$?
	cd && sudo ldconfig
	err=err+$? 
