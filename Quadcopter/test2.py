
from dronekit import connect, Command, LocationLocal, Vehicle, VehicleMode
from pymavlink import mavutil
import time, argparse, math, sys
#import dronekit_sitl


#Using simulator. 
#sitl = dronekit_sitl.start_default()
#ns = sitl.connection_string()

#Connecting to the vehicle. 
parser = argparse.ArgumentParser(description="Connecting to the drone with port 14553")
parser.add_argument('--connect', help='Connect to the vehicle using this port.')
args = parser.parse_args()
cns = args.connect
print "Connecting to : %s" % cns
drone = connect(cns, wait_ready=None)
print drone.mode

def PX4setMode():
    drone._master.mav.command_long_send(drone._master.target_system, drone._master.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0, 88, 0, 0, 0, 0, 0, 0)


#Px4 settings mode.
#PX4setMode(GUIDED)
PX4setMode()
print "Mode set"
print "Vehicle Armed ? : %s" % drone.armed
while 1:
    print "Vehicle Altitude: %s" % drone.location.local_frame
    print drone.mode
    print "Vehicle Armed ? : %s" % drone.armed
    time.sleep(2)
