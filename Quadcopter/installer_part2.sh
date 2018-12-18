#!/bin/bash
	while true;
	do 
     	echo -------------------------------------------------------------
        declare -i err
	err=0
	echo Cloning RCBenchmark repositories and changing working directory.
        cd
        cd /home/pi/Transport_Protocol
        sudo git checkout Transport_Protocol-V2
        err=err+$?
	sudo git pull
	err=err+$?
        echo -------------------------------------------------------------
           echo Creating auto launching scripts
        cd
        mkdir autolaunch_scripts
        cd
        (crontab -l ; echo "@reboot screen -d -m -L /home/pi/autolaunch_scripts/mavproxy.log sh /home/pi/autolaunch_scripts/launch_mavproxy_rcb.sh") | sort - | uniq - | crontab -
        err=err+$?
	sleep 0.1
	(crontab -l ; echo "@reboot screen -d -m -L /home/pi/autolaunch_scripts/pose.log sh /home/pi/autolaunch_scripts/launch_pose_forward_rcb.sh") | sort - | uniq - | crontab -
        err=err+$?
	sleep 0.1
	(crontab -l ; echo "@reboot screen -d -m sh /home/pi/autolaunch_scripts/launch_OLED_screen.sh") | sort - | uniq - | crontab -
        err=err+$?
	sleep 0.1
        (crontab -l ; echo "@reboot screen -d -m sh /home/pi/autolaunch_scripts/launch_c9.sh") | sort - | uniq - | crontab -
        echo Setting up autolaunch_scripts folder
        sudo cp /home/pi/Transport_Protocol/Quad_Environment/launch_mavproxy_rcb.sh /home/pi/autolaunch_scripts
        err=err+$?
	sudo cp /home/pi/Transport_Protocol/Quad_Environment/launch_pose_forward_rcb.sh /home/pi/autolaunch_scripts
	err=err+$?
        sudo cp /home/pi/Transport_Protocol/Quad_Environment/launch_OLED_screen.sh /home/pi/autolaunch_scripts
        err=err+$?
	sudo cp /home/pi/Transport_Protocol/Quad_Environment/launch_c9.sh /home/pi/autolaunch_scripts
        err=err+$?
	echo Setup Complete! 
        sleep 0.2
        if [ $err -gt 0 ];
	then
	echo RCB_Transport_Protocol installation failed. 
	fi
	echo Making Files executable
        sudo chmod +x ~/autolaunch_scripts/launch_mavproxy_rcb.sh
        err=err+$?
	sudo chmod +x ~/autolaunch_scripts/launch_pose_forward_rcb.sh
        sudo chmod +x ~/autolaunch_scripts/launch_OLED_screen.sh
        err=err+$?
	sudo chmod +x ~/autolaunch_scripts/launch_c9.sh
        err=err+$?
	echo Creating log deleting scripts
        sudo sed -i '$i \rm ~/Desktop/pose.log' /etc/rc.local
        err=err+$?
	sudo sed -i '$i \rm ~/Desktop/mavproxy.log' /etc/rc.local
        cd && sudo apt-get -y install curl
	sudo apt-get -y install libcurl4-openssl-dev
	err=err+$?
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
	echo Dronecode cloned and installed.
        echo -------------------------------------------------------------
        echo Installing Cmake
        sudo apt-get -y install cmake 
        err=err+$?
	if [ $err -gt 0 ];
	then
	echo Auto Launch Scripts or DronecodeSDK failed
	break
	fi
	echo -------------------------------------------------------------
        echo All dependencies installed
        echo -------------------------------------------------------------
        echo Preparing to reboot 
        echo you have 5 seconds to cancel. to cancel press Ctl+C
        sleep 5
	break
	done
        
