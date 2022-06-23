from pymongo import MongoClient
from instructions import Instructions
from bson import ObjectId
from time import sleep
import datetime
from random import randint
import subprocess
#import RPi.GPIO as GPIO
import gpio
import config
from ping import ping



user = 'root'
password = 'root'
ip = '192.167.100.105'
add = 'mongodb://192.167.100.105:27017/'
port = 27017

# panel index
pi = 0

# change this variable to modify the time between each update
time_before_update = 1


# TODO: replace with host VPN IP adress and Mongodb port when on RP
client = MongoClient(add)

# database connexion
db = client.portNS
# db.authentificate = (user, password)

oldInstruction = ""

print("Python app running\n"
      "Connected to MongoDB\nIP : " + ip + " \nPort : " + str(port))

# init bash command for hdmi control
bashCommand = ["xrandr --output HDMI-1 --off", "xrandr --output HDMI-1 --auto",
               "cat /sys/class/thermal/thermal_zone0/temp"]
#bashCommand = ["ls", "ls", "ls"]

# initialisation du PANEL pour post
PANEL = {"isOpen": False,
         "name": "Init",
         "screen": True,
         "online": True,
         "state": True,
         "temperature": 0,
         "index": 0,
         "date": datetime.datetime.utcnow()}

hasBeenDisconnected = False

while (1):

    # to handle disconnection with server

    resp = ping("192.167.100.105")

    if resp and not hasBeenDisconnected:
        print('### DISCONNECTED FROM SERVER ###')
        print('### DISABLING HDMI ###')
        # process = subprocess.Popen(bashCommand[0].split(), stdout=subprocess.PIPE)
        # output, error = process.communicate()
        hasBeenDisconnected = True
    elif not resp and hasBeenDisconnected:
        print('### RECONNECTED TO SERVER ###')
        print('### ENABLING HDMI ###')
        # process = subprocess.Popen(bashCommand[1].split(), stdout=subprocess.PIPE)
        # output, error = process.communicate()
        hasBeenDisconnected = False



    # collection fetching
    panelLogs = db.panellogs
    instructions = db.instructions.find()
    panels = db.panels.find()

    # fetching instructions into a class
    panelInst = Instructions(instructions)

    # applying instructions
    if panelInst.table[pi]['instruction'] != panels[pi]['state']:
        if panelInst.table[pi]['instruction']:
            # script on
            print('### HDMI PORT ENABLED ###')
            process = subprocess.Popen(bashCommand[1].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            # print(output, error)
            # updating old status with new instructions
            status = True
            postPANEL = panelLogs.insert_one(PANEL).inserted_id
            # changing LED states
            gpio.change_output(status)
            # last log
            print('#################################')
            print('Last log :')
            for key, value in PANEL.items():
                print('---------------------------------')
                print(key, ":", value)
            print('#################################')
        elif not panelInst.table[pi]['instruction']:
            # script off
            print('### HDMI PORT DISABLED ###')
            process = subprocess.Popen(bashCommand[0].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            # print(output, error)
            # updating old status with new instructions
            status = False
            postPANEL = panelLogs.insert_one(PANEL).inserted_id
            # changing LED states
            gpio.change_output(status)
            # last log
            print('#################################')
            print('Last log :')
            for key, value in PANEL.items():
                print('---------------------------------')
                print(key, ":", value)
            print('#################################')
    else:
        status = panels[pi]['state']

    print("Status :", panels[pi]['state'])

    # getting panel measures
    # TODO: functions to get measures from panel instruments
    #
    # Temp function
    process = subprocess.Popen(bashCommand[2].split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    # temperature = 0
    temperature = int(output)/1000

    door_1, door_2, online = gpio.update_input()
    # printing results
    print("Door 1 :", door_1)
    print("Door 2 :", door_2)
    print("Les portes sont fermées" if door_1 and door_2 else "Au moins une porte est ouverte")
    print("Power :", online)

    # checking if anything goes wrong
    if not(door_1 and door_2) or not(online) or (temperature >= 80):
        bug = True
    else:
        bug = False
    print("Bug :", bug)
    # put request to panel state
    putPANEL = db["panels"].find_one_and_update(
        {"_id": ObjectId(panels[pi]['_id'])},
        {"$set":
             {'state': status,
              'temperature': temperature,
              'door_1': not door_1,
              'door_2': not door_2,
              'screen': online,
              'bug': bug},
         }, upsert=True
    )

    # pushing instructions into logs
    PANEL = {"door_1": putPANEL['door_1'],
         "door_2": putPANEL['door_2'],
         "name": putPANEL['name'],
         "screen": putPANEL['screen'],
         "online": putPANEL['online'],
         "state": putPANEL['state'],
         "temperature": putPANEL['temperature'],
         "index": putPANEL['index'],
         "date": datetime.datetime.utcnow()}

    if temperature > 70:
        postPANEL = panelLogs.insert_one(PANEL).inserted_id
        print("TEMPERATURE : > 70")
    # wait time before update
    sleep(time_before_update)
