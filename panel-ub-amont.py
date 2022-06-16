from pymongo import MongoClient
from instructions import Instructions
from bson import ObjectId
from time import sleep
import datetime
from random import randint

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
    # TODO: script to control HDMI port
    if panelInst.table[pi]['instruction'] != panels[pi]['state']:
        if panelInst.table[pi]['instruction']:
            # script on
            print('### ENABLING HDMI PORT ###')
        else:
            # script off
            print('### DISABLING HDMI PORT ###')

    # updating old status with new instructions
    newPan = []
    if panels[pi]['index'] == pi + 1:
        panels[pi]['state'] = panelInst.table[pi]['instruction']
        newPan.append(panels[pi])

    # getting panel measures
    # TODO: functions to get measures from panel instruments
    # Temp function
    newTemp = [0, 0, 0]
    newTemp[0] = randint(0, 100)

    # put request to panel state
    putPANEL = db["panels"].find_one_and_update(
        {"_id": ObjectId("62a887b519cacf3ab907126f")},
        {"$set":
             {'state': newPan[0]['state'],
              'temperature': newTemp[0]},
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

    postPANEL

    # print('#########################')
    #
    # print('Last log :')
    #
    # for key, value in PANEL.items():
    #     print(key, ":", value, ";")
    # print('#########################')
    # wait time before update
    sleep(time_before_update)
