# ==============================================================================
# Made by Ellen Schuchert (es225ib)
# imports and global varibles

from network import WLAN
import urequests as requests
import time
from keys import ubidots_tokein, wifi_password, Wifi_SSID
import machine
from machine import I2C, Pin, ADC
import ssd1306
import pycom

TOKEN = ubidots_tokein #Put your TOKEN here
DELAY = 180 # Delay in seconds
delaySendTime = 0
celsius = 0
light = 0

# ==============================================================================
#Connectes to wifi

wlan = WLAN(mode=WLAN.STA)
wlan.antenna(WLAN.INT_ANT)

# Assign your Wi-Fi credentials
wlan.connect(Wifi_SSID, auth=(WLAN.WPA2, wifi_password), timeout=5000)

while not wlan.isconnected ():
    machine.idle()
print("Connected to Wifi\n")
pycom.heartbeat(False)

# ==============================================================================
# Builds the json to send the request
def build_json(variable1, value1, variable2, value2):
    try:
        data = {variable1: {"value": value1},
                variable2: {"value": value2,}}
        return data
    except:
        return None

# Sends the request. Please reference the REST API reference https://ubidots.com/docs/api/
def post_var(device, value1, value2):
    try:
        url = "https://industrial.api.ubidots.com/"
        url = url + "api/v1.6/devices/" + device
        headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
        data = build_json("Temperature", value1, "Light", value2)
        if data is not None:
            print(data)
            req = requests.post(url=url, headers=headers, json=data)
            return req.json()
        else:
            pass
    except:
        pass

# ==========================================================================
# set pins, aktivate an I2C channel and declere a display

pycom.rgbled(0xFF0000) # RED color, the built in LED is used to se if anything goes wrong in the set up in the "field"

#set the temperature pin
adc = machine.ADC(bits=10)
tempPin = adc.channel(pin='P16')

#set the light LightSensorPin, taken from the example given by the TAs
lightPin = Pin('P15', mode=Pin.IN)  # set up pin mode to input
analogLightPin = adc.channel(attn=ADC.ATTN_11DB, pin='P15')   # create an analog pin on P16;  attn=ADC.ATTN_11DB measures voltage from 0.1 to 3.3v

i2c = I2C(0, I2C.MASTER, baudrate=100000, pins=("P9","P10"))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

pycom.rgbled(0x00FF00) #green
#=============================================================================
# funktions used in main code

# draws desired figure on the display, this funktions is written by Mohammad Qasem a TA
def draw_figure(display, shape, x=0, y=0, c = None):
    for i, row in enumerate(shape):
        for j, c in enumerate(row):
            display.pixel((j+x), i+y, c)

# erases desired figure, I modifed Mohammads funktion
def erase_figure(oled, shape, x=0, y=0):
    for i, row in enumerate(shape):
        for j, c in enumerate(row):
            c = not c
            oled.pixel(j+x, i+y, 0)

# cheks the temperature 5 times and returns the avrage
def check_temp():
    avrage_Temp = 0
    celsius = 0
    for i in range(5):
         millivolts = tempPin.voltage()
         celsius = (millivolts - 400.0)/19.5            # I have used the values for the MCP9701 as I found that to work better, consider changing to - 500.0 and /10 instead. 
         avrage_Temp += celsius
         time.sleep(0.2)                                # wait a litte
    return int(avrage_Temp/(5))

#  cheks the photoresistor 5 times and returns the avrage
def check_light():
    avrage_Light = 0
    for i in range(5):
        avrage_Light += analogLightPin.value()
        time.sleep(0.2)
    return int(avrage_Light/5)
#==========================================================================
# display figures based on images found online, but modified and coded into 1 and 0 by me

panda = [[0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0],
       [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
       [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
       [1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1],
       [1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1],
       [1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1],
       [1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1],
       [1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1],
       [0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0],
       [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
       [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
       [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
       [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
       [0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0],
       [0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0],
       [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]]

sun = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0],
       [0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],
       [0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0],
       [0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
       [1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
       [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0],
       [0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
       [0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
       [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

snowflake = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0],
           [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
           [0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0],
           [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0],
           [0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0],
           [0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0],
           [0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
           [0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0],
           [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
           [0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0],
           [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
           [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

#==========================================================================
# draw permanent objects on the display
draw_figure(display, panda, 5, 30)
display.text("Temperature:", 27, 20, 1)
display.text("Light is:", 50, 40, 1)
display.invert(True)  #invret the screen to make my panda normal

# ==========================================================================
# main code
while True:
    display.text(str(celsius), 54, 30, 0)       # clear old temp value from screen
    display.text(str(light), 52, 50, 0)         # clear old temp value from screen

    celsius = check_temp()                      # chek temperature value
    light = check_light()                       # get lightValue

    if celsius > 30:                            # dispaly sun or snowflake depending on the temperature (30 or 10 degree celsius)
        draw_figure(display, sun, 5, 5)
    elif celsius < 10:
        draw_figure(display, snowflake, 5, 5)
    else:                                       # clear sun or snowflake if in normal range
        erase_figure(display, snowflake, 5, 5)
        erase_figure(display, sun, 10, 10)


    print("Temperature is ", celsius, '\n', "Light is ", light)           # just for controll
    display.text(str(celsius), 54, 30, 1)       # display temp on display
    display.text(str(light), 52, 50, 1)         # display temp on display
    display.show()

    if delaySendTime == 3 :                     #sends the collected data to ubibots every nine minutes
        post_var("pycom", celsius, light)
        delaySendTime = 0                       # reset the delaySendTime

    delaySendTime += 1                          #Delay for sending data to ubidots
    time.sleep(DELAY)                           #Sleeps

#==========================================================================
