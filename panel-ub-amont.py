from pymongo import MongoClient
from instructions import Instructions
from bson import ObjectId
from time import sleep
import datetime
from random import randint
import subprocess

ip = 'localhost'
port = 27017

# panel index
pi = 2

# change this variable to modify the time between each update
time_before_update = 10

# TODO: replace with host VPN IP adress and Mongodb port when on RP
client = MongoClient(port=port)

oldInstruction = ""

print("Python app running\n"
      "Connected to MongoDB\nIP : " + ip + " \nPort : " + str(port))

# init bash command for hdmi control
# bashCommand = ["xrandr --output HDMI-1 --off", "xrandr --output HDMI-1 --auto"]
bashCommand = ["ls", "ls"]

while (1):

    # database connexion
    db = client.portNS

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
            print('### ENABLING HDMI PORT ###')
            process = subprocess.Popen(bashCommand[1].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            # print(output, error)
            # updating old status with new instructions
            status = True
        else:
            # script off
            print('### DISABLING HDMI PORT ###')
            process = subprocess.Popen(bashCommand[0].split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            # print(output, error)
            # updating old status with new instructions
            status = False
    else:
        status = panels[pi]['state']

    print("PANEL STATUS =", status)


    # getting panel measures
    # TODO: functions to get measures from panel instruments
    # Temp function

    # put request to panel state
    putPANEL = db["panels"].find_one_and_update(
        {"_id": ObjectId(panels[pi]['_id'])},
        {"$set":
             {'state': status,
              'temperature': randint(0, 100)},
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

    postPANEL = panelLogs.insert_one(PANEL).inserted_id

    # print('#########################')
    #
    # print('Last log :')
    #
    # for key, value in PANEL.items():
    #     print(key, ":", value, ";")
    # print('#########################')
    # wait time before update
    sleep(time_before_update)
