from luma.core.interface.serial import i2c
from luma.oled import device
from luma.oled.device import ssd1306
from PIL import Image
import time, socket, os
from luma.core.render import canvas
from luma.core.virtual import viewport


# Initializing Display
serial = i2c(port=1, address=0X3c)
device = ssd1306(serial, rotate=2)
vision_error = False
# Displaying RCB logo
def rcb_logo():
    frameSize = (128,64)
    filename = "/home/pi/Transport_Protocol/UDP/LCD_Python/RCbenchmark.ppm"
    image = Image.open(filename).resize((128,64), Image.ANTIALIAS).convert('1')
    image.show()
    device.display(image)
    time.sleep(3)
    return

# Drawing on screen
def draw_onscreen(x, y, text):
    global vision_error  
    ip_addr = IP_Addr()
    if text == ip_addr:
        with canvas(device) as draw:
            draw.text((0,0), "IP:"+ IP, fill="white")
            draw.text((0,30), id, fill="white")
    elif ip_addr == "127.0.0.1":
        with canvas(device) as draw:
            draw.text((0,0), "Internet offline", fill="white")
    else:
        ip_addr = IP_Addr()
        with canvas(device) as draw:
            #if "192.168.1" in a:
             #   a = "Incorrect Router"
            draw.text((0,0),"IP:"+ ip_addr, fill="white")
            draw.text((x, y), text, fill="white")
            draw.text((0,30), id, fill="white")
            if vision_error == True:
                draw.text((0,45), "Vision & IMU mismatch", fill="white")
            #Used for displaying user message. P.S. Limited to 21 characters for now. 
            #draw.text((0,45), "Enter your text here", fill = "white")
    time.sleep(1)

# Scrolling on the screen
def draw_scroll(text):
    IP = IP_Addr()
    text_size = len(text) + 42
    virtual = viewport(device, width= device.width, height= device.height)
    letter_scroll = 1
    scroller = 0
    while letter_scroll in range(text_size):
        with canvas(virtual) as draw:
            draw.text((0,0),"IP:"+IP, fill="white")
            draw.text((10 - a*3, 15), text, fill="white")       
        letter_scroll += 1
        if  letter_scroll == text_size:
            letter_scroll = 0
            scroller += 1
            if scroller >= 2: 
                pose = os.path.isfile('/home/pi/autolaunch_scripts/pose.log')
                draw_onscreen(0,15, "Rechecking...")
                break
    launch_Check()
    
# Displaying Device IP Address
def IP_Addr():
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
def rcb_TrackingCheck():
    global vision_error
    while True:
        pose = os.path.isfile('/home/pi/autolaunch_scripts/pose.log')
        if pose == True:
            file_size = os.path.getsize("/home/pi/autolaunch_scripts/pose.log")
            time.sleep(2)
            file_size_new = os.path.getsize("/home/pi/autolaunch_scripts/pose.log")
            if file_size == file_size_new:            
                draw_onscreen(0, 15, "TrackingLab Offline")
                file_size = os.path.getsize("/home/pi/autolaunch_scripts/pose.log")
                draw_onscreen(0,15, "Updating Status...")
                os.remove("/home/pi/autolaunch_scripts/pose.log")
            else:
                draw_onscreen(0,15, "Receiving Data!")
                with open("/home/pi/autolaunch_scripts/pose.log") as reading_file:
                    for line in reading_file:
                        if "Vision" in line:
                            vision_error = True
                            draw_onscreen(0,15, "Receiving Data!")
                            break
                    os.remove("/home/pi/autolaunch_scripts/pose.log")
                    vision_error = False
                    time.sleep(1)
                draw_onscreen(0,15, "Updating Status...")
        else:
            draw_scroll("Position Forward not running")


# Checking if the necessary files are launched.

def launch_Check():
    mavproxy = os.path.isfile('/home/pi/autolaunch_scripts/mavproxy.log')
    pose = os.path.isfile('/home/pi/autolaunch_scripts/pose.log')
    if mavproxy == True:
        draw_onscreen(0,15, "MavProxy Launched")
        if pose == True:
            draw_onscreen(0,15, "PoseForward Launched")
            found = False
            with open("/home/pi/autolaunch_scripts/pose.log") as reading_file:
                for line in reading_file:
                    if '>>> No heartbeat in 30 seconds, aborting.' in line:
                        os.remove("/home/pi/autolaunch_scripts/pose.log")
                        draw_scroll("Not Linked to Mavproxy")
                        found = True
                        break
                    elif 'socket.error: [Error 101] Network is unreachable' in line:
                        draw_onscreen(0, 15, "Not Connected to Q.G.C.")
                        found = True
                        time.sleep(1)
                        draw_onscreen(0,15, "Checking for Q.G.C")                        
                        os.remove("/home/pi/autolaunch_scripts/pose.log")
                        launch_Check()
                        break
                    elif 'Keyboard' in line:
                        draw_onscreen(0,15, "User aborted")
                        os.remove("/home/pi/autolaunch_scripts/pose.log")
                        launch_Check()
                    elif 'Data received' in line:
                        break   
                    
            if found != True:
                draw_onscreen(0,15, "Linked to MavProxy")
                #rcb_TrackingCheck()
        else:
            draw_scroll("PoseForward Not Launched")
    else:
        draw_scroll("MavProxy not launched")
    return found


def controller_id():
    with open("/home/pi/autolaunch_scripts/launch_mavproxy_rcb.sh") as data:
        line = data.read()
        words = line.split()
        if "--controller-id" in words[-1]:
            temp = words[-1].split("=")
            cont_id ="Tracker ID: " +temp[1]
            return cont_id
        else:
            return " " 


# Calling all the functions in order
if __name__ == '__main__':
    id = controller_id()
    rcb_logo()
    IP = IP_Addr()
    while IP == '127.0.0.1':
        with canvas(device) as draw:
            draw.text((0,0), "Internet Offline", fill="white")
        IP = IP_Addr()
    draw_onscreen(0, 0, IP)
    launch_check_result = launch_Check()
    if launch_check_result == False:
        rcb_TrackingCheck()
