from pymavlink import mavutil
import os,time
vehicle = mavutil.mavlink_connection('127.0.0.1:14553', dialect='common')
print mavutil.current_dialect
print (vehicle.wait_heartbeat())
print mavutil.mavlink20()

print mavutil.location(0,0,0)
#bob = mavutil.mavfile(vehicle)
#bob.set_mode_auto()
#mavutil.set_mode_px4(220,0,0)
print "Arming"
vehicle.mav.command_long_send(vehicle.target_system,vehicle.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,1,0,0,0,0,0,0)
time.sleep(2)
vehicle.mav.command_long_send(vehicle.target_system,vehicle.target_component,mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,0,0,0,0,0,0,0,0.1)
time.sleep(4)
vehicle.mav.command_long_send(vehicle.target_system,vehicle.target_component,84,0,0,0,0,1,0b0000111111111000,-0.1,0,0,0.02,0,0,0,0,0,0,0)
time.sleep(4)
vehicle.mav.command_long_send(vehicle.target_system,vehicle.target_component,mavutil.mavlink.MAV_CMD_NAV_LAND,0,0,0,0,0,0,0,0)
time.sleep(6)
vehicle.mav.command_long_send(vehicle.target_system,vehicle.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,0,0,0,0,0,0,0)
print "Disarmed"
#vehicle.mav.message_factory.set_position_target_local_ned_encode(0,0,0,1,0xFFFF,0,0,0,0,0,0.4,0,0,0,0,0)
print mavutil.current_dialect
