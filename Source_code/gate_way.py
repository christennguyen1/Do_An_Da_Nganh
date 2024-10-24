import serial.tools.list_ports
import random
import time
import sys
from Adafruit_IO import MQTTClient


AIO_USERNAME = "Vinhnguyen2003"
AIO_KEY = "aio_SLKq65Rrse9Bs7AEz7EQreMn2AYg"
AIO_FEED_ID = ["nutnhan1", "nutnhan2", "va-tem", "va-lux", "va-pir", "relay", "pump"]

def connected (client) :
    print ("Ket noi thanh cong...")
    for feed in AIO_FEED_ID :
        client.subscribe(feed)


def subscribe ( client , userdata , mid , granted_qos ) :
    print ("Subcribe thanh cong...")

def disconnected ( client ) :
    print ("Ngat ket noi...")
    sys.exit (1)
    
def message ( client , feed_id , payload ):
    print ("Nhan du lieu : " + feed_id + " - " + payload )
    if isMicrobitConnected and "va" in feed_id :
        print("!" + str( feed_id ) + "_" + str( payload ) + "#")
        ser.write (("!" + str( feed_id ) + "_" + str( payload ) + "#") . encode () )
    else:
        print("!" + str( feed_id ) + "-" + str( payload ) + "#")
        ser.write (("!" + str( feed_id ) + "-" + str( payload ) + "#") . encode () )

def getPort () :
    ports = serial.tools.list_ports.comports ()
    N = len ( ports )
    commPort = "None"
    for i in range (0 , N) :
        port = ports [ i ]
        strPort = str ( port )
        if "USB" in strPort :
            splitPort = strPort.split (" ")
            commPort = ( splitPort [0])
    return commPort

isMicrobitConnected = False
if getPort () != "None":
    global ser 
    ser = serial.Serial ( port = getPort () , baudrate =115200)
    isMicrobitConnected = True


def processData ( data ) :
    data = data.replace ("!", "")
    data = data.replace ("#", "")
    splitData = data.split (":")
    splitDataValue = splitData[1].split("-")
    tem = splitDataValue[0].split("_")[1]
    hum = splitDataValue[1].split("_")[1]
    lux = splitDataValue[1].split("_")[1]
    print( tem, ' - ', hum, ' - ', lux)
    if tem != "":
        client.publish ("temperture", tem)
        print("Publish temperture successful")
    if hum != "":
        client.publish ("humidity", hum)
        print("Publish humidity successful")
    if lux != "":
        client.publish ("light", lux)  
        print("Publish light successful")


mess = ""
def readSerial () :
    bytesToRead = ser.inWaiting()
    if ( bytesToRead > 0) :
        global mess
        mess = mess + ser.read( bytesToRead ).decode ("UTF-8")
        while ("#" in mess ) and ("!" in mess ) :
            start = mess.find ("!")
            end = mess.find ("#")
            processData ( mess [ start : end + 1])
            if ( end == len( mess )) :
                mess = ""
            else :
                mess = mess[ end + 1:]



client = MQTTClient ( AIO_USERNAME , AIO_KEY )
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect ()
client.loop_background ()


while True :
    readSerial ()
    time.sleep (1)