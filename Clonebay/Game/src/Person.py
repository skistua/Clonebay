##Add standard Header
from random import randint

class Person:
    def __init__(self, de, person_id, race='human'):
        self.race = race
        self.id = person_id
        
        #sexytime
        sex_id = randint(0, len(de.names) - 1)
        i = 0         
        #feel free to add more, if you like.  FTL only supports 'male' and 'female',  you would need to figure out how to name additional options
        for k, v in de.names.items():
            if i == sex_id:
                self.sex = k
                break 
            i += 1
            
        
        randomizer = randint(0, len(de.names[self.sex]) - 1)
        self.name = de.names[self.sex][randomizer]
        
        self.anim = {}
        for anim in de.anims:
            if anim['sheet'] == race:
                self.anim[anim['@name']] = anim
        for animsheet in de.animSheets:
            if animsheet['@name'] == race:
                self.anim_sheet = animsheet
                    
        self.hp = 100
        self.damage = 10
        self.repair_speed = 10
        self.move_speed = 10
        
        
        self.skills = {'pilot': 0,
                       'engine': 0,
                       'shield': 0,
                       'weapon': 0,
                       'repair': 0,
                       'fight': 0
                       }
        self.stats = {'jumps': 0,
                      'shots_fired': 0,
                      'piloted_evasions': 0,
                      'engine_evasions': 0,
                      'shots_blocked': 0,
                      'repairs': 0,
                      'kills': 0
                      }
