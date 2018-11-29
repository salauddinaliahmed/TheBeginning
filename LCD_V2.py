from luma.core.interface.serial import i2c
from luma.oled import device
from luma.oled.device import ssd1306
from PIL import Image
import time, socket, os
from luma.core.render import canvas
from luma.core.virtual import viewport
import subprocess as sp
import RCB_pose_forward as rpf

# Initializing Display
serial = i2c(port=1, address=0X3c)
device = ssd1306(serial, rotate=2)

# Displaying RCB logo
def rcb_logo():
    frameSize = (128,64)
    filename = "/home/pi/Transport_Protocol/UDP/LCD_Python/RCbenchmark.ppm"
    image = Image.open(filename).resize((128,64), Image.ANTIALIAS).convert('1')
    image.show()
    device.display(image)
    time.sleep(5)
    return

# Drawing on screen
def draw_onscreen(x, y, text):
    a = IP_Addr()
    if text == a:
        with canvas(device) as draw:
            draw.text((0,0), "IP:"+ IP, fill="white")
            draw.text((0,30), id, fill="white")
    elif a == "127.0.0.1":
        with canvas(device) as draw:
            draw.text((0,0), "Internet offline", fill="white")
    else:
        a = IP_Addr()
        with canvas(device) as draw:
            #if "192.168.1" in a:
             #   a = "Incorrect Router"
            draw.text((0,0),"IP:"+ a, fill="white")
            draw.text((x, y), text, fill="white")
            draw.text((0,30), id, fill="white")
            #Used for displaying user message. P.S. Limited to 21 characters for now. 
            #draw.text((0,45), "Enter your text here", fill = "white")
    time.sleep(2)

# Scrolling on the screen
def draw_scroll(text):
    text_size = len(text) + 42
    virtual = viewport(device, width= device.width, height= device.height)
    a = 1
    scroller = 0
    while a in range(text_size):
        with canvas(virtual) as draw:
            draw.text((0,0),"IP:"+IP, fill="white")
            draw.text((10 - a*3, 15), text, fill="white")       
        a += 1
        if a == text_size:
            a = 0
            scroller += 1
            if scroller >= 2: 
                # mavproxy = os.path.isfile('/home/pi/Desktop/mavproxy.log')
                # pose = os.path.isfile('/home/pi/Desktop/pose.log')
                draw_onscreen(0,15, "Rechecking...")             
                break
    launch_check()
    
# Displaying Device IP Address
def ip_addr():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('192.168.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    if IP == '127.0.0.1':
        IP = "Internet Offline"
      #  while IP == '127.0.0.1':
       #     with canvas(device) as draw:
        #        draw.text((0,15), "Not Connected to Internet.")
         #   IP = IP_Addr()  
    return str(IP)


# Checking if RCB Tracking Lab connectivity:
# def rcb_TrackingCheck():
#     file_size = os.path.getsize("/home/pi/Desktop/pose.log")
#     time.sleep(2)
#     while True:
#         file_size_new = os.path.getsize("/home/pi/Desktop/pose.log")
#         if file_size == file_size_new:            
#             draw_onscreen(0, 15, "TrackingLab Offline")
#             file_size = os.path.getsize("/home/pi/Desktop/pose.log")
#             draw_onscreen(0,15, "Updating Status...")

#         else:
#             draw_onscreen(0,15, "Receiving Data!")
#             file_size = os.path.getsize("/home/pi/Desktop/pose.log")
#             time.sleep(0.2)
#             draw_onscreen(0,15, "Updating Status...")


# # Checking if the necessary files are launched.

# def launch_Check():
#     mavproxy = os.path.isfile('/home/pi/Desktop/mavproxy.log')
#     pose = os.path.isfile('/home/pi/Desktop/pose.log')
#     if mavproxy == True:
#         draw_onscreen(0,15, "MavProxy Launched")
#         if pose == True:
#             draw_onscreen(0,15, "PoseForward Launched")
#             found = False
#             with open("/home/pi/Desktop/pose.log") as reading_file:
#                 for line in reading_file:
#                     if '>>> No heartbeat in 30 seconds, aborting.' in line:
#                         os.remove("/home/pi/Desktop/pose.log")
#                         draw_scroll("Not Linked to Mavproxy")
#                         found = True
#                         break
#                     elif 'socket.error: [Error 101] Network is unreachable' in line:
#                         draw_onscreen(0, 15, "Not Connected to Q.G.C.")
#                         found = True
#                         time.sleep(4)
#                         draw_onscreen(0,15, "Checking for Q.G.C")                        
#                         os.remove("/home/pi/Desktop/pose.log")
#                         launch_Check()
#                         break
#                     elif 'Keyboard' in line:
#                         draw_onscreen(0,15, "User aborted")
#                         os.remove("/home/pi/Desktop/pose.log")
#                         launch_Check()
#                     elif 'Data received' in line:
#                         break   
                    
#             if found != True:
#                 draw_onscreen(0,15, "Linked to MavProxy")
#                 rcb_TrackingCheck()
#         else:
#             draw_scroll("PoseForward Not Launched")
#     else:
#         draw_scroll("MavProxy not launched")


def controller_id():
    with open("/home/pi/Desktop/launch_mavproxy_rcb.sh") as data:
        line = data.read()
        words = line.split()
        if "--controller-id" in words[-1]:
            a = words[-1].split("=")
            cont_id ="Tracker ID: " +a[1]
            return cont_id
        else:
            return " " 


# Code to check if a process is active using subprocess and ps shell cmd
def launch_check():
    #Checking if mavproxy is launched
    process_list = sp.check_output("ps -u | grep mavproxy.py", shell=True, universal_newlines=True)
    mavproxy = list(process_list.split('\n', 1)[0].split())
    if mavproxy[10] == "/usr/bin/python":
        draw_onscreen(0, 15, "Mavproxy Launched")
    else:
        draw_scroll("Mavproxy Not Launched")
    
    #Checking if pose_forward is launched
    process_list = sp.check_output("ps -u | grep RCB_pose_forward.py", shell=True, universal_newlines=True)
    pose = list(process_list.split('\n', 1)[0].split())
    if pose[10] == "python":
        draw_onscreen(0, 15, "PoseForward Launched")
        # Function to check if Position is being forwarded and received by the script
        rcb_trackingcheck()
    else:
        draw_onscreen(0, 15, "PoseForward Error")
    
def rcb_trackingcheck():
    while True:
        process_list = sp.check_output("ps -u | grep RCB_pose_forward.py", shell=True, universal_newlines=True)
        pose = list(process_list.split('\n', 1)[0].split())
        if pose[7] == "Sl+" or pose[2]>33:
            draw_onscreen(0, 15, "TrackingLab Offline")
            time.sleep(2)
        elif len(pose) == 0:
            draw_onscreen(0, 15, "PoseForward Relaunching")
            time.sleep(2)
        else: 
            draw_onscreen(0, 15, "Receiving Data!")
            time.sleep(2)
        draw_onscreen(0, 15, "Updating Status...")
        if rpf.ekf_callback.ekf_status == False:
            draw_onscreen(0,15, "EKF error!")




# Calling all the functions in order
if __name__ == '__main__':
    id = controller_id()
    rcb_logo()
    IP = ip_addr()
    while IP == '127.0.0.1':
        with canvas(device) as draw:
            draw.text((0,0), "Internet Offline", fill="white")
        IP = ip_addr()
    draw_onscreen(0, 0, IP)
    launch_check()
    # add this comment
    
