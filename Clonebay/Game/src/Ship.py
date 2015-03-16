##Ship class




class Ship:
    def __init__(self, bp):
        self.blueprint = bp
        #get all the data from the blueprint, and cast it correctly
        self.id = bp['@name']
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
        
        self.rooms = bp['layout']['rooms']
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
                             
        
    
        