from dronekit import connect, Command, LocationLocal, Vehicle, VehicleMode
from pymavlink import mavutil
import time, argparse, math, sys
#import dronekit_sitl


#Using simulator 
#sitl = dronekit_sitl.start_default()
#ns = sitl.connection_string()

#Setting up modes and their values.
Guided = 88 #Disarmed.
GuidedArmed = 216
Takeoff = 22 #TakeOff of the drone.
#LAND = 21 #Command for landing the drone.


#Connecting to the vehicle. 
parser = argparse.ArgumentParser(description="Connecting to the drone with port 14553")
parser.add_argument('--connect', help='Connect to the vehicle using this port.')
args = parser.parse_args()
cns = args.connect
print "Connecting to : %s" % cns
drone = connect(cns, wait_ready=None)
a=drone.message_factory.set_position_target_local_ned_encode(0,0,0,mavutil.mavlink.MAV_FRAME_LOCAL_NED,0xFFFF,0,0,-0.5,0,0,0,0,0,0,0,0)
drone.send_mavlink(a)
#drone.mode = VehicleMode('OFFBOARD')
#drone._master.mav.command_long_send(drone._master.target_system,drone._master.target_component,mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0, 216, 0,0,0,0,0,0)
#drone.armed = True
#msg=drone.message_factory.set_position_target_local_ned_encode(0,0,0,mavutil.mavlink.MAV_FRAME_LOCAL_NED,(0x1000 | 0b100111000000),0,0,-0.3,0,0,0.1,0,0,0,0,0)
#drone.send_mavlink(msg)
def PX4setMode(mavMode):
    drone._master.mav.command_long_send(drone._master.target_system, drone._master.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,mavMode, 0,0, 0, 0, 0, 0)

#Take off message. 
def takeoff(alt):
    drone.armed = True
    #drone._master.mav.command_long_send(0, 0, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF_LOCAL, 0, 0, 0, 0, 0, 0, 0, -alt)
    #drone.mode = VehicleMode('OFFBOARD')
    a=drone._master.mav.set_local_position_setpoint_encode(0,0,1,0,0,-0.5,0)
    drone.send_mavlink(a)
    #drone.simple_takeoff(0.4)
    #PX4setMode(Takeoff)
   # drone._master.mav.command_long_encode(0,0,MAV_CMD_NAV_GUIDED_ENABLED,1,0,0,0,0,0,0,0)
   # msg1=drone.
    msg=drone.message_factory.set_position_target_local_ned_encode(0,0,0,mavutil.mavlink.MAV_FRAME_LOCAL_NED, (0x1000 | 0b100111000000),0,-alt,-alt,0,0,0,0,0,0,0,0)
    #msg=drone.message_factory.mav_cmd_nav_takeoff_local_encode(0,0,0.2,0,0,0,-0.6)
    #drone.send_mavlink(msg)
    time.sleep(0.2)
    print "Message sent"
    while True:
        print(" Altitude: ", abs(drone.location.local_frame.down))
        # Break and return from function just below target altitude.
        if abs(drone.location.local_frame.down) >= abs(alt) * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

#Switching to Landing
def land():
    drone._master.mav.command_long_send(0, 0, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, 0, 0)
    

#Px4 settings mode Guided Disarmed.

#Px4 settings mode Armed Guided.
PX4setMode(GuidedArmed)

#Taking off
drone.airspeed=0.1
takeoff(0.3)
#print "Vehicle Altitude: %s" % drone.location.local_frame
time.sleep(4)
print ("Land mode executed.")
land()
time.sleep(3)
print "Vehicle Altitude: %s" % drone.location.local_frame
