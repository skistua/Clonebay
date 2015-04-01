from src.GamepackLoader import loadGamepacks
from src.world_gen import genWorld
from random import randint
from asyncio import events

class DataEngine:
    def tick(self):
        pass
    
    def continueGame(self):
        pass
    
    def newGame(self, difficulty, playerShipBlueprint):
        self.game_data['difficulty'] = difficulty
        
        self.world_map = genWorld(self.game_data)
        self.player['score'] = 0
        self.player['shipsDefeated'] = 0
        self.player
        
        #This is very unpythonic.
        self.i = 0
        self.j = 0
        while self.i < len(self.world_map):
            while self.j < len(self.world_map[self.i]['beacons']):
                if self.j != 10000:
                    mapEvent = self.world_map[self.i]['beacons'][self.j]['event']
                    mapEvent = self.load_event(mapEvent)
                    

                
                    if 'choice' in mapEvent:
                        mapEvent['choices'] = []
                    
                        ##This is fscking stupid.
                        while len(mapEvent['choice']) > 0:
                            try:
                                mapEvent['choices'].append(mapEvent['choice'].pop())
                                #NOOOOOOO!!!!    
                            except(TypeError):
                                mapEvent['choices'].append(mapEvent['choice'])
                                break
                         
                        ### Don't need these prints, but this might come up again.    
                        #for choice in mapEvent['choices']:
                        #    try:
                        #        print('\t'+choice['text'])
                        #    except(TypeError):
                        #        try:
                        #            choice['text'] = choice['text']['#text']
                        #            print('\t ALMOST ERROR: #text'+choice['text'])
                        #        except(KeyError):
                        #            print("ERROR!!!")
                        #            print(choice)
                                
                        
                    if 'shipBlueprint' in mapEvent:
                        print(mapEvent['shipBlueprint'])
        
                self.world_map[self.i]['beacons'][self.j]['event'] = mapEvent
                
                self.j = self.j + 1
            self.i = self.i + 1
            self.j = 0
    
    def buildListByType(self, data_type):
        self.data_items = []
        bad_tags = ['@name', '@auto_blueprint', 'escape', 'gotaway', 'destroyed', 'deadCrew', 'text']
        for gameFile in self.game_data.items():
            try:
                if(any(data_type in item for item in gameFile)):
                    listy = list(gameFile) #THIS IS STUPID!  DON'T DO THIS! USE DICTRIGHT!
                    if data_type in listy[1]:
                        for data_item in listy[1][data_type]:
                            
                            #BUG CLEANER
                            if data_item in bad_tags:
                                pass
                            else:
                               
                                self.data_items.append(data_item)
            except(TypeError):
                pass            
        return self.data_items
    
    def load_ship(self, ship):
        pass
    
    def find_event(self, id):
        for eventList in self.eventlists:
            try:
                if eventList['@name'] == id:
                    self.eventList = eventList['event']
                    self.randomizer = randint(0, len(eventList) - 1)
                    self.selected_event = self.eventList[self.randomizer]
                    
                    #for event in self.events:
                    #    if event['@name'] == self.event_id:
                    #        return event
                    if 'choice' in self.selected_event:
                        self.selected_event['choices'] = []
                    
                        ##This is fscking stupid.
                        while len(self.selected_event['choice']) > 0:
                            try:
                                self.selected_event['choices'].append(self.selected_event['choice'].pop())
                                #NOOOOOOO!!!!    
                            except(TypeError):
                                self.selected_event['choices'].append(self.selected_event['choice'])
                                break
                    return self.selected_event
            except:
                print(eventList)            
                 
            
    
    def load_event(self, meta_event):
        if 'event' in meta_event:
            max_item = len(meta_event['event']) - 1
            randomizer = randint(0, max_item)
            new_event = ''
            try:
                new_event =  meta_event['event'][randomizer]['@load']
            except(KeyError):
                new_event =  meta_event['event']['@load']
            for event in self.events:
                if event['@name'] == new_event:
                    meta_event = event
                    break
                    
        if 'text' not in meta_event:
            meta_event['text'] = 'ERROR: NOT FOUND!'
            print ("NO TEXT ENTRY FOR META_EVENT")
            return meta_event
        if '@load' in meta_event['text']:
            for textList in self.textLists:
                if textList['@name'] == meta_event['text']['@load']:
                    max_item = len(textList['text']) - 1
                    rand_text = randint(0, max_item)
                    meta_event['text'] = textList['text'][rand_text]
                    break
            else:
                print("TEXT LOOK UP FAILED FOR " + meta_event['text'])
        if 'ship' in meta_event:
            for shipEvent in self.shipEvents:
                if shipEvent['@name'] == meta_event['ship']['@load']:
                    meta_event['shipEvent'] = shipEvent
                    for blueprintList in self.blueprintLists:
                        if shipEvent['@auto_blueprint'] == blueprintList['@name']:
                            max_ship = len(blueprintList['name']) - 1
                            rand_ship = randint(0, max_ship)
                            shipBlueprintName = blueprintList['name'][rand_ship]
                            for shipBlueprint in self.shipBlueprints:
                                if shipBlueprint['@name'] == shipBlueprintName:
                                    meta_event['shipBlueprint'] = shipBlueprint
                                    break
                            else:
                                print("NOT FOUND: " + shipBlueprintName)
                            break
                    else:
                        for shipBlueprint in self.shipBlueprints:
                                if shipBlueprint['@name'] == shipEvent['@auto_blueprint']:
                                    meta_event['shipBlueprint'] = shipBlueprint
                                    break
                        else:
                            print("NOT FOUND!")
                    break
            else:
                print("error")
        
        return meta_event
            
    def __init__(self):
   
        self.gamepacks = loadGamepacks()
        self.gamepack = self.gamepacks['FTL']
        self.game_data = self.gamepack['data']['gamedata']
        self.events = self.buildListByType('event')
        self.eventlists = self.buildListByType('eventList')
        self.textLists = self.buildListByType('textList')
        self.shipEvents = self.buildListByType('ship')
        self.shipBlueprints = self.buildListByType('shipBlueprint')
        self.blueprintLists = self.buildListByType('blueprintList')
        self.roomLayouts = self.buildListByType('roomLayout')
        self.augBlueprints = self.buildListByType('augBlueprint')
        self.droneBlueprints = self.buildListByType('droneBlueprint')
        self.systemBlueprints = self.buildListByType('systemBlueprint')
        self.weaponBlueprints = self.buildListByType('weaponBlueprint')
        self.itemBlueprints = self.buildListByType('itemBlueprint')
        self.crewBlueprints = self.buildListByType('crewBlueprint')
        self.sectorDescriptions = self.buildListByType('sectorDescription')
        self.sectorTypes = self.buildListByType('sectorType')
        self.anims = self.buildListByType('anim')
        self.animSheets = self.buildListByType('animSheet')
        self.weaponAnims = self.buildListByType('weaponAnim')
        
    ##TODO Handle overwrites
    
        #keep player as dict or create class?
        self.player = {}
    
    #associate each blueprint with its layout
        for shipBlueprint in     self.shipBlueprints:
        #PLAYER_SHIP_ANAEROBIC_3 should not have been uncommented in data files.
            try:
                shipBlueprint['layout'] = self.game_data[shipBlueprint['@layout']]
            except(KeyError):
                print("whoops!")
    
        self.names = {}
        for nameList in self.game_data['names']['nameList']:
            self.names[nameList['@sex']] = []  #intentionally left ambiguous.  FTL only includes 'male' and 'female'
        for nameList in self.game_data['names']['nameList']:
            for person_name in nameList['name']:
                try:
                    print(nameList['@sex'] + ': ' + person_name)
                    self.names[nameList['@sex']].append(person_name)
                except:
                    print(nameList['@sex'] + ': ' + person_name['#text'])
                    self.names[nameList['@sex']].append(person_name['#text'])
                    
    
 
