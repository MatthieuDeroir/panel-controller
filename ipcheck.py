from ping import ping
from time import sleep
from pymongo import MongoClient
from bson import ObjectId


sleep_time = 10
add = 'mongodb://192.167.100.105:27017/'
client = MongoClient(add)
# database connexion
db = client.portNS

online = [True, True, True]

while (1):
    panels = db.panels.find()

    isIndretOnline = ping("192.167.100.123")
    isAvalOnline = ping("192.167.100.123")
    isAmontOnline = ping("192.167.100.123")

    print(isIndretOnline)
    print(isAvalOnline)
    print(isAmontOnline)

    if isIndretOnline == 0:
        online[0] = True
    else:
        online[0] = False

    if isAvalOnline == 0:
        online[1] = True
    else:
        online[1] = False

    if isAmontOnline == 0:
        online[2] = True
    else:
        online[2] = False

    bug = not online[0] or not online[1] or not online[2]
    print(bug)


    putPANEL = db["panels"].find_one_and_update(
        {"_id": ObjectId(panels[0]['_id'])},
        {"$set":
             {'online': online[0],
              'bug': bug},
         }, upsert=True
    )
    putPANEL = db["panels"].find_one_and_update(
        {"_id": ObjectId(panels[1]['_id'])},
        {"$set":
             {'online': online[1],
              'bug': bug},
         }, upsert=True
    )
    putPANEL = db["panels"].find_one_and_update(
        {"_id": ObjectId(panels[2]['_id'])},
        {"$set":
             {'online': online[2],
              'bug': bug},
         }, upsert=True
    )

    sleep(sleep_time)

