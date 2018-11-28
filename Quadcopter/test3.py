from dronekit import connect, Command, LocationLocal, Vehicle, VehicleMode 
from pymavlink import mavutil
import time, argparse, math, sys
#import dronekit_sitl


#Using simulator 
#sitl = dronekit_sitl.start_default()
#ns = sitl.connection_string()

#Setting up modes and their values.
Guided = 88 #Disarmed.
GuidedArmed =216 
#Takeoff = 22 #TakeOff of the drone.
#LAND = 21 #Command for landing the drone.


#Connecting to the vehicle. 
parser = argparse.ArgumentParser(description="Connecting to the drone with port 14553")
parser.add_argument('--connect', help='Connect to the vehicle using this port.')
args = parser.parse_args()
cns = args.connect
print "Connecting to : %s" % cns
drone = connect(cns, wait_ready=None)

def PX4setMode(mavMode):
    print mavMode
    drone._master.mav.command_long_send(drone._master.target_system, drone._master.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0, mavMode, 0, 0, 0, 0, 0, 0)
#Take off message. 
def takeoff():
   # a= drone.MAVLink.set_mode_encode(drone._master.target_system,8,0)
   # drone.set_mode_send(a)
    PX4setMode(GuidedArmed)
    time.sleep(3)
    drone.armed = True
    msg=drone.message_factory.set_position_target_local_ned_encode(0,0,0,mavutil.mavlink.MAV_FRAME_LOCAL_NED,(0x1000 | 0b100110000011),0,0,-0.6,0,0,0,0,0,0,0,1)
    drone.send_mavlink(msg)
    time.sleep(3)
    land()

#Switching to Landing
def land():
    msg=drone.message_factory.set_position_target_local_ned_encode(0,0,0,mavutil.mavlink.MAV_FRAME_LOCAL_NED, (0x2000|0b110111000111),0,0,0,0,0,0,0,0,0,0,0)

takeoff()

