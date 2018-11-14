
"""
This code base has been taken from  https://github.com/dronekit/dronekit-python.git and changes were made.
"""


from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative, mavutil, mavlink



# Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    print (vehicle.location.local_frame)
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", abs(vehicle.location.local_frame.down))
        # Break and return from function just below target altitude.
        if abs(vehicle.location.local_frame.down) >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


arm_and_takeoff(0.5)

#print("Set default/target airspeed to 3")
vehicle.airspeed = 0.2

print("Take off successful!")
print ("----------------Current Location---------")
print (vehicle.location.global_relative_frame)
print (vehicle.location.local_frame)
print ("----------------End of Current Location---------")
#exit()

# sleep so we can see the change in map
time.sleep(3)

def goto_position_target_local_ned(north, east, down):
    """
    Send SET_POSITION_TARGET_LOCAL_NED command to request the vehicle fly to a specified
    location in the North, East, Down frame.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
        0b0000111111111000, # type_mask (only positions enabled)
        north, east, down,
        0, 0, 0, # x, y, z velocity in m/s  (not used)
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
    # send command to vehicle
    vehicle.send_mavlink(msg)
    print ("message sent")

# print("Going towards second point for 30 seconds (groundspeed set to 10 m/s) ...")
# point2 = vehicle.location.local_frame.north + 2 
# #point2 = LocationGlobalRelative(-35.363244, 149.168801, 20)
# vehicle.simple_goto(point2, groundspeed=10)

# sleep so we can see the change in map

# Moving toward North. Sending a mavlink message to move forward. 

print ("Sailing north")
east_now = vehicle.location.local_frame.east
down_now = vehicle.location.local_frame.down
goto_position_target_local_ned(0.5, east_now, down_now)
print ("------------------ Moving ------------")
print (vehicle.location.local_frame)
print ("Current north north direction: ", vehicle.location.local_frame.north)

time.sleep(6)

print ("----------------------checking if the vechicle is moving forward----------------------")
print (vehicle.location.local_frame)
print ("In the north direction: ", vehicle.location.local_frame.north)

time.sleep(5)

print ("------------------are you holding position-------------")
print (vehicle.location.local_frame)
print ("In the north direction: ", vehicle.location.local_frame.north)

east_now = vehicle.location.local_frame.east
down_now = vehicle.location.local_frame.down
goto_position_target_local_ned(-0.5, east_now, down_now)
print ("------------------ Moving Backward------------")
print (vehicle.location.local_frame)
print ("Current north north direction: ", vehicle.location.local_frame.north)


time.sleep(5)

print("Initialing Landing sequence.")
vehicle.mode = VehicleMode("LAND")
print (vehicle.location.local_frame)
# Close vehicle object before exiting script

time.sleep(3)

print("Close vehicle object")
print ("After landing the drone is at position: ", vehicle.location.local_frame)
# Shut down simulator if it was started.
if sitl:
    sitl.stop()