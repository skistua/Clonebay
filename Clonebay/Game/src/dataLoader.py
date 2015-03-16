import xmltodict
import os, glob
from pathlib import Path
import re
import collections
from _pickle import dump



def loadGameData(data_path):
    """Loads all game data"""
    game_data = collections.OrderedDict()
    filenames = []
    usedfiles = []
    
    #The ships have additional files that are not xml
    ships = {}
    for filename in data_path.glob("*.txt"):
        ship = {}  
        print(filename)    
        print(filename.parent)
            #remove the ".xml"
        shipFile = filename.name[:-4]
        shipXML = filename.parent.joinpath(shipFile + ".xml")
            #remove the "../data/"
        print(shipXML)
        print(shipFile)
    
        
        roomCount = 0
        doorCount = 0
        if shipFile != "credits":
                
            with shipXML.open() as f:
                data = f.read()
                data = re.sub('-{3,}', '--', data)
                    #turn it into valid xml so the parser doesn't choke on the comments and lack of encapuslating tag
                data = "<"+shipFile+">" + data + "</" + shipFile + ">"
                    #print(eventFile)
                obj = xmltodict.parse(data)
            
                ships[shipFile] = obj[shipFile]
                f.close()
                usedfiles.append(shipXML)
                
            with filename.open() as f:
                ships[shipFile]["rooms"] = {}
                ships[shipFile]["doors"] = {}
                while True:
                    line = f.readline()
                    if not line: 
                        break
                    if line == "X_OFFSET\n":
                        tmp = f.readline()
                        inti = int(tmp[:-1])
                        ships[shipFile]["x_offset"] = inti
                    elif line == "Y_OFFSET\n":
                        ships[shipFile]["y_offset"] = int(f.readline()[:-1])
                    elif line == "VERTICAL\n":
                        ships[shipFile]["vertical"] = int(f.readline()[:-1])
                    elif line == "HORIZONTAL\n":
                        ships[shipFile]["horizontal"] = int(f.readline()[:-1])
                    elif line == "ELLIPSE\n":
                        ellipse = {}
                        ellipse["width"] = int(f.readline()[:-1])
                        ellipse["height"] = int(f.readline()[:-1])
                        ellipse["x-offset"] = int(f.readline()[:-1])
                        ellipse["y-offset"] = int(f.readline()[:-1])
                        ships[shipFile]["ellipse"] = ellipse
                    elif line == "ROOM\n":
                        room = {}
                        room["id"] = int(f.readline()[:-1])
                        room["x"] = int(f.readline()[:-1])
                        room["y"] = int(f.readline()[:-1])
                        room["w"] = int(f.readline()[:-1])
                        room["h"] = int(f.readline()[:-1])
                        ships[shipFile]["rooms"][roomCount] = room
                        roomCount = roomCount + 1
                    elif line == "DOOR\n":
                        door = {}
                        door["id"] = doorCount
                        door["x"] = int(f.readline()[:-1])
                        door["y"] = int(f.readline()[:-1])
                        door["roomLU"] = int(f.readline()[:-1])
                        door["roomRD"] = int(f.readline()[:-1])
                        door["vertical"] = int(f.readline()[:-1])
                        ships[shipFile]["doors"][doorCount] = door
                        doorCount = doorCount + 1
                    else:
                        print("error parsing line: " + line)
                f.close()
                usedfiles.append(filename) 

    game_data.update(ships)
    for filename in data_path.glob("*.xml"):
        #make sure it's not one of the ship files we already used
        if filename not in usedfiles:
            filenames.append(filename)

    
    data = ""    
    for filename in filenames:    
        #remove the ".xml"
        basename = filename.stem
        
        
        with filename.open() as f:
            data = f.read()
            
            data = re.sub('-{3,}', '--', data)
            #turn it into valid xml so the parser doesn't choke on the comments and lack of encapuslating tag
            print(basename)
            data = "<"+basename+">" + data + "</"+basename+">"
            f.close()
            usedfiles.append(filename)
            obj = xmltodict.parse(data)
            game_data.update(obj)
    
              
    return game_data      
              