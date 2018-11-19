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
def takeoff(alt):
    PX4setMode(GuidedArmed)
    time.sleep(3)
    drone._master.mav.command_long_send(0, 0, 24, 0, 0, 0, 0.3, 0, 0, 0,-alt)
    msg=drone.message_factory.set_position_target_local_ned_encode(0,0,0, mavutil.mavlink.MAV_FRAME_LOCAL_NED,(0x1000|0b110111000011),0,0,0,0,0,0,0,0,0,0,-0.5)
    drone.send_mavlink(msg)
    #msg=drone._master.mav.command_ack_send(24,1)
    #print msg
    #a= Command(0,0,0,0, 22, 0,1,0,0,0,0,0,0,alt)
    #drone.commands.add(a)
    print "Message sent"
    print drone.mode
    print drone.mode
    while True:
        print(" Altitude: ", abs(drone.location.local_frame.down))
        print drone.mode
        # Break and return from function just below target altitude.
        if abs(drone.location.local_frame.down) >= abs(alt) * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)
#Switching to Landing
def land():
    drone._master.mav.command_long_send(0, 0, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, 0, 0)
    

#Px4 settings mode Guided Disarmed.
#PX4setMode(Guided)
print drone.armed
#Px4 settings mode Armed Guided.
drone.armed = True
PX4setMode(GuidedArmed)
print drone.armed
time.sleep(3)
#Taking off
takeoff(1.5)
print "Second Vehicle Altitude: %s" % drone.location.local_frame
time.sleep(4)
land()
time.sleep(3)
print "Vehicle Altitude: %s" % drone.location.local_frame
