from pymongo import MongoClient
from instructions import Instructions
from bson import ObjectId
from time import sleep
import datetime
from random import randint
import subprocess

# import RPi.GPIO as GPIO


user = 'root'
password = 'root'
ip = '192.167.100.105'
add = 'mongodb://192.167.100.105:27017/'
port = 27017

# panel index
pi = 2

# change this variable to modify the time between each update
time_before_update = 10

# config de la numérotation GPIO
# GPIO.setmode(GPIO.BCM)

# index des entrées
door_1_index = 2
door_2_index = 3
power_index = 4

GPIO = ''

# configuration des broches
GPIO.setup(door_1_index, GPIO.IN)
GPIO.setup(door_2_index, GPIO.IN)
GPIO.setup(power_index, GPIO.IN)


# TODO: replace with host VPN IP adress and Mongodb port when on RP
client = MongoClient(add)

oldInstruction = ""

print("Python app running\n"
      "Connected to MongoDB\nIP : " + ip + " \nPort : " + str(port))

# init bash command for hdmi control
 bashCommand = ["xrandr --output HDMI-1 --off", "xrandr --output HDMI-1 --auto", "cat /sys/class/thermal/thermal_zone0/temp"]
bashCommand = ["ls", "ls", "ls"]

# initialisation du PANEL pour post
PANEL = {"isOpen": False,
         "name": "Init",
         "screen": True,
         "power": True,
         "state": True,
         "temperature": 0,
         "index": 0,
         "date": datetime.datetime.utcnow()}

while (1):

    # database connexion
    db = client.portNS
    # db.authentificate = (user, password)

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
        elif not panelInst.table[pi]['instruction']:
            # script off
            print('### HDMI PORT DISABLED ###')
            process = subprocess.Popen(bashCommand[0].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            # print(output, error)
            # updating old status with new instructions
            status = False
            postPANEL = panelLogs.insert_one(PANEL).inserted_id
    else:
        status = panels[pi]['state']

    print("Status :", panels[pi]['state'])

    # getting panel measures
    # TODO: functions to get measures from panel instruments
    #
    # Temp function
    process = subprocess.Popen(bashCommand[2].split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    temperature = int(output)/1000

    temperature = 0
    # Power measure
    power = GPIO.input(power_index)
    # Door measure
    door_2 = GPIO.input(door_2_index)
    door_1 = GPIO.input(door_1_index)
    # put request to panel state
    putPANEL = db["panels"].find_one_and_update(
        {"_id": ObjectId(panels[pi]['_id'])},
        {"$set":
             {'state': status,
              'temperature': temperature,
              'power': power,
              'isOpen': door_1 and door_2
              }
         }, upsert=True
    )

    # pushing instructions into logs
    PANEL = {"isOpen": putPANEL['isOpen'],
         "name": putPANEL['name'],
         "screen": putPANEL['screen'],
         "power": putPANEL['power'],
         "state": putPANEL['state'],
         "temperature": putPANEL['temperature'],
         "index": putPANEL['index'],
         "date": datetime.datetime.utcnow()}

    #postPANEL = panelLogs.insert_one(PANEL).inserted_id

    print('#################################')

    print('Last log :')

    for key, value in PANEL.items():
        print('---------------------------------')
        print(key, ":", value)

    print('#################################')

    # wait time before update
    sleep(time_before_update)
