##Ship class




class Ship:
    def __init__(self, bp, de):
        self.blueprint = bp
        #get all the data from the blueprint, and cast it correctly
        self.id = bp['@name']
        print("loading ship: " + self.id)
        self.basename = bp['@img']
        self.base_image_name = self.basename +'_base'
        if 'floorImage' in bp:
            self.floor_image_name = bp['floorImage'] + '_floor'
        else: 
            self.floor_image_name = self.basename + '_floor'
            
        if 'shieldImage' in bp:
            self.shield_image_name = bp['shieldImage']+ '_shields1'
        else:
            self.shield_image_name = self.basename + '_shields1'
        
        
        self.crew = []
        #add the crew
        
        self.drone_slots = int(bp['droneSlots'])
        self.drones = []
        #add the drones
        
        
        #add the gibs
        self.gibs = []
        self.gibsTemp = bp['layout']['explosion']
        for gib_old, giblet in self.gibs:
            gib = {}
            gib['imageName'] = self.basename + '_' + gib_old
            for k, v in gib_old:
                gib[k] = {max: float(giblet[k]['@max']),
                          min: float(giblet[k]['@min'])}
            self.gibs.append(gib)
        self.tiles = []
        self.ship_systems = {}
        self.rooms = bp['layout']['rooms']
        for k, room in self.rooms.items():
            room['x_pix'] =  35 * room['x']
            room['y_pix'] = 35 * room['y']
            room['w_pix'] = 35 * room['w']
            room['h_pix'] = 35 * room['h']
            room['loc'] = (room['x_pix'], room['y_pix'])
            room['tiles'] = []
            i = 0
            j = 0
            
            while i < room['w']:
                while j < room['h']:
                    tile = (room['x_pix'] + i * 35, room['y_pix'] + j * 35)
                    room['tiles'].append(tile)
                    self.tiles.append(tile)
                    j += 1
                j = 0
                i += 1
            
            
            
            
            for system_name, ship_system in bp['systemList'].items():
                if int(ship_system['@room']) == room['id']:
                    
                    #fed cruisers don't have start tags on artillery.  They should start with them.
                    for k, v in ship_system.items():
                        if k == '@start':
                            break
                    else:
                        print(self.id + ': ' + system_name + "is missing start tag")
                        ship_system['@start'] = 'true'
                        
                    if ship_system['@start'] == 'true':
                        print(system_name)
                        room['system'] = {}
                        room['system']['name'] = system_name
                        if '@img' not in ship_system: 
                            print('no img tag found for ' + system_name) #
                            room['image'] = 'room_' + system_name
                        else:
                            room['image'] = ship_system['@img']
                        for systemBlueprint in de.systemBlueprints:
                            if systemBlueprint['@name'] == system_name:
                                self.ship_systems[system_name] = ship_system
                                self.ship_systems[system_name]['blueprint'] = systemBlueprint
                                break
                        
                    else:
                        break
            
            

                
                        
                    
        
        self.doors = bp['layout']['doors']
            
        self.layout = bp['layout']
        self.health = int(bp['health']['@amount'])
        try:
            self.desc = bp['desc']
        except:
            print(self.id + 'has no description.')
        self.class_name = bp['class']
        self.max_power = int(bp['maxPower']['@amount'])
        self.name = bp['name']
        self.ellipse = bp['layout']['ellipse']
        self.floor_offset = {'x': int(bp['layout']['offsets']['floor']['@x']), 
                             'y': int(bp['layout']['offsets']['floor']['@y'])}
        self.cloak_offset = {'x': int(bp['layout']['offsets']['cloak']['@x']), 
                              'y': int(bp['layout']['offsets']['cloak']['@y'])}
                             
        
    
        