import argparse
import time

import sys
import socket
import array
import struct
from dronekit import connect, VehicleMode
from client_udp import RCbenchmark_pkg
import math


parser = argparse.ArgumentParser(description='Forward RCBenchmark Tracking lab messages to MavProxy or to a Pixhahk')
parser.add_argument('--out', default='127.0.0.1:14552', help='String specifying the out connection. Eg. 127.0.0.1:14551 (default), or /dev/ttyS0')
parser.add_argument('--port', default=5401, type=int , help='Port to listen to for incoming pose messages')
parser.add_argument('--controller_id', default=None, type=str , help='Port to listen to for incoming pose messages')

args = parser.parse_args()
 
id = args.controller_id
print (id)
vehicle = connect(args.out, wait_ready=None)
vehicle.wait_ready('autopilot_version')

#Callback definition for mode observer
def mode_callback(self, attr_name):
    print ("Vehicle Mode", self.mode)

#Add observer callback for attribute `mode`
vehicle.add_attribute_listener('mode', mode_callback)


# Listen to certain messages
# @vehicle.on_message('LOCAL_POSITION_NED')
#def listener(self, name, message):
#     print ('message: %s' % message)
# print(" Altitude: ", vehicle.location.global_relative_frame.alt)


# We are trying to send VISION_POSITION_ESTIMATE ( #102 ) and VISION_SPEED_ESTIMATE ( #103 )


# IP Address - on Linux verify by typing : $ hostname -I
# 127.0.0.1 is the localhost loopback address. Use if RCbenchmark
# tracking lab is running on the same machine.
# The IP is not retreived automatically
# UDP_IP = '127.0.0.1' 

# This is a trick to obtain the local LAN address 192.168.X.XXX
s= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
UDP_IP = s.getsockname()[0]
s.close()

BUFSIZE = 184  # buffer size is 184 bytes

UDP_PORT = args.port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet. UDP.

sock.bind(('', UDP_PORT))  # bind socket

rcbenchmark_pkg = RCbenchmark_pkg()  # empty object

timeout = time.time() + 20   # 5 minutes from now
print(UDP_IP)
def main():
    while True:
        print('Waiting for datagram ...')
        #print(sock.recvfrom(BUFSIZE))
        (data, addr) = sock.recvfrom(BUFSIZE)  # buffer size is 184 bytes
        print('Data received')
        doubles_sequence = array.array('d', data)
        rcbenchmark_pkg.update_data(doubles_sequence)
        #if sys.byteorder == 'little':
            # rcbenchmark_pkg.print_udp_pkg()
        #   print(rcbenchmark_pkg.lin_pos_x)
        # else:

            # "big"

        #   doubles_sequence.byteswap()  # swap byte order to match little-endian
        #   rcbenchmark_pkg.print_udp_pkg()
        #print('Received datagram.\n')

        def quaternion_euler(w, x, y, z):
            t0 = +2.0 * (w * x + y * z)
            t1 = +1.0 - 2.0 * (x * x + y * y)
            roll = math.atan2(t0, t1)
	
            t2 = +2.0 * (w * y - z * x)
            t2 = +1.0 if t2 > +1.0 else t2
            t2 = -1.0 if t2 < -1.0 else t2
            pitch = math.asin(t2)
	
            t3 = +2.0 * (w * z + x * y)
            t4 = +1.0 - 2.0 * (y * y + z * z)
            yaw = math.atan2(t3, t4)
	
            return roll,pitch,yaw

        roll, pitch, yaw = quaternion_euler(rcbenchmark_pkg.quaternion_w,rcbenchmark_pkg.quaternion_x, rcbenchmark_pkg.quaternion_y, rcbenchmark_pkg.quaternion_z)
    
        if id == None or id == "fill the controller id here":#controller id:
            msg = vehicle.message_factory.vision_position_estimate_encode(
                rcbenchmark_pkg.timestamp,  # Timestamp (microseconds, synced to UNIX time or since system boot),
                rcbenchmark_pkg.lin_pos_x, -rcbenchmark_pkg.lin_pos_y, -rcbenchmark_pkg.lin_pos_z, roll, -pitch, -yaw)
        #msg = vehicle.message_factory.att_pos_mocap_encode(
        #       rcbenchmark_pkg.timestamp,  # Timestamp (microseconds, synced to UNIX time or since system boot)
        #      [rcbenchmark_pkg.quaternion_w,rcbenchmark_pkg.quaternion_x, rcbenchmark_pkg.quaternion_y, rcbenchmark_pkg.quaternion_z],
        #     rcbenchmark_pkg.lin_pos_x, -rcbenchmark_pkg.lin_pos_y, -rcbenchmark_pkg.lin_pos_z) # x, y, z
        # send command to vehicle
            vehicle.send_mavlink(msg)
            #print ("If block executed")
        #print(rcbenchmark_pkg.timestamp)
        # print('msg sent')

def ekf_callback(self, attr_name, msg):
    ekf_status = msg
    
vechile.add_attribute_listener('ekf_ok', ekf_callback)


print("Close vehicle object")
vehicle.close()

if __name__=="__main__":
    main()  
