from collections import OrderedDict
import random
import src.xmltodict
from random import randint
from src.dataLoader import loadGameData





def buildSectorMap(game_data, events, eventLists):
    sectorDescriptions = []
    sectorTypes = []
    realSD = game_data['sector_data']
    total = 0
    sectorCount = 1
    start_sector_name = 'CIVILIAN_SECTOR'
    for gameFile in game_data.items():
        try:    
            if(any("sectorType" in item for item in gameFile)):
                listy = list(gameFile)
                for sectorType in listy[1]['sectorType']:
                    sectorTypes.append(sectorType)
            if(any("sectorDescription" in item for item in gameFile)):
                listy = list(gameFile)
                for sectorDescription in listy[1]['sectorDescription']:
                    sectorDescriptions.append(sectorDescription)
        except(TypeError):
            pass
    startSector = {}
    for desc in sectorDescriptions:
        if desc['@name'] == start_sector_name:
            startSector = desc 
            break
    else: print("ERROR: START SECTOR: " + start_sector_name + " not found!")
            
    sectorMap = {}    
    
    sectorMap[0] = buildSector(startSector, 1, game_data, events, eventLists)
    sectorCount = sectorCount + 1
    total=total + 1
    desc = ""
    while(sectorCount < 8):
        minsector = 1000
        randSector = randint(0, len(sectorDescriptions) - 1)
        while (minsector > sectorCount) and desc != 'CRYSTAL HOME': 
            randSector = randint(0, len(sectorDescriptions) - 1)
            minsector = int(sectorDescriptions[randSector]['@minSector'])
            desc = sectorDescriptions[randSector]['@name']
            print (desc)

        
        sectorMap[total] = buildSector(sectorDescriptions[randSector], sectorCount, game_data, events, eventLists)
        total = total + 1
        sectorCount = sectorCount + 1
    
    return sectorMap

def buildSector(description, sectorNum, game_data, events, eventLists):
    sector = {}
    sector['description'] = description
    sector['beacons'] = []
    totalBeacons = 1    
    
    #build the start beacon    
    #MISSING: CIV SECTOR START: "Welcome to a new sector! Get to the exit beacon and jump to the next sector before the pursuing Rebels catch you!"
    startEvent = {}
    startEventName = ""
    if sectorNum == 1:
        startEventName = 'START_GAME'
    else:
        startEventName = description['startEvent']
    
 
    for event in events:
        if event['@name'] == startEventName:
            startEvent = event
            break
    else:
        print("error -- event: " + startEventName + " not found!")
    sector['beacons'].append(buildBeacon(startEvent, random.randint(0,150), -1))
    sector['beacons'][0]['id'] = 0
    
    #add the other beacons from the template  
    for metaEvent in description['event']:
        randAdd = random.randint(0, int(metaEvent['@max']) - int(metaEvent['@min']))
        count = int(metaEvent['@min']) + randAdd
        counter = 0
        beacon_event = {}
        for event in events:
            if event['@name'] == metaEvent['@name']:
                beacon_event = event
                break
        else:
            for eventList in eventLists:
                if '@name' in eventList:
                    if eventList['@name'] == metaEvent['@name']:
                        beacon_event = eventList
                        break
            else:
                print("error -- event: " + metaEvent['@name'] + " not found!")
        
    
        while counter < count:
                    beacon = buildBeacon(beacon_event, -1, -1)
                    beacon['id'] = totalBeacons
                    sector['beacons'].append(beacon)
                    totalBeacons = totalBeacons + 1
                    counter = counter + 1

        
    #TODO: add exit beacon
    
    #connect the dots
    for beacon in sector['beacons']:
        
        beacon['connections'] = []
        for other_beacon in sector['beacons']:
            if other_beacon == beacon:
                pass
            else:
                xdiff = beacon['x'] - other_beacon['x']
                ydiff = beacon['y'] - other_beacon['y']
                if (-300 < xdiff < 300):
                    if (-300 < ydiff < 300):
                        beacon['connections'].append(other_beacon['id'])
                                        
    #todo:  pathfinding to make sure all nodes are accessible    
    return sector



def buildBeacon(event, x, y):
    beacon = {}
    if x == -1:
        beacon["x"] = randint(0, 700)
    else: 
        beacon["x"] = x
    if y == -1:
        beacon["y"] = randint(0, 450)
    else:
        beacon["y"] = y
    beacon['event'] = event
    return beacon


def genWorld(game_data):
    events = []
    for gameFile in game_data.items():
        try:
            if(any("event" in item for item in gameFile)):
                listy = list(gameFile)
                if "event" in listy[1]:
                    for event in listy[1]['event']:
                        events.append(event)
        except(TypeError):
            pass
    eventLists = []
    for gameFile in game_data.items():
            try:
                if(any("eventList" in item for item in gameFile)):
                    listy = list(gameFile)
                    if "eventList" in listy[1]:
                        for eventList in listy[1]['eventList']:
        
                            if eventList == '@name':
                                pass
                            elif eventList == 'event' :
                                pass
                            else:
                                eventLists.append(eventList)
            except(TypeError):
                pass

    map = buildSectorMap(game_data, events, eventLists)
    return map







