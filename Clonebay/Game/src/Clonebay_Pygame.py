import pygame, math, sys, os, time
from pygame.locals import * 
from pygame import Rect
from pygame import draw
from random import randint

from src.dataEngine import DataEngine
from src.Ship import Ship

BLACK = (0,0,0)
WHITE = (255, 255, 255)
YELLOW = (255,255, 0)
FLOOR = (230, 226, 219)
TILEBORDER = (172, 169, 164)




### from www.pygame.org/wiki/TextWrap

# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = Rect(rect)
    y = rect.top
    lineSpacing = -2
 
    # get the height of the font
    fontHeight = font.size("Tg")[1]
 
    while text:
        i = 1
 
        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break
 
        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1
 
        # if we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1
 
        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)
 
        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing
 
        # remove the text we just blitted
        text = text[i:]
 
    return text, y


def initPlayerShip(ps, de):
    ps.base_image = pygame.image.load(str(de.gamepack['img'][ps.base_image_name])).convert_alpha()
    ps.base_rect = ps.base_image.get_rect()
    ps.floor_image = pygame.image.load(str(de.gamepack['img'][ps.floor_image_name])).convert_alpha()
    ps.floor_rect = ps.floor_image.get_rect()
    ps.tiles_offset = ((ps.floor_rect.w - ps.width) / 2, (ps.floor_rect.h - ps.height)/2)
    for k, room in ps.rooms.items():
        room['rect'] = Rect(room['x_pix'], room['y_pix'], room['w_pix'], room['h_pix'])
        for key, v in room.items():
            if key == 'image':
                try:
                    room['roomimage'] = pygame.image.load(str(de.gamepack['img'][room['image']])).convert_alpha()
                    room['imagerect'] = room['roomimage'].get_rect()
                    break
                    
                except(KeyError):
                    print('image not found: ' + room['image'])
        for key, v in room.items():
            if key == 'system':
                room['system_image'] = pygame.image.load(str(de.gamepack['img']['s_' + room['system']['name'] + '_overlay'])).convert_alpha()
                room['system_image_rect'] = room['system_image'].get_rect()
                break
            

def blitPlayerShip(ps, location, screen, de):
    # NEED TO CHECK VISIBILITY
    ps.base_rect.center = location
    screen.blit(ps.base_image, ps.base_rect)
    
        
    ps.floor_location = (ps.floor_offset['x'] + ps.base_rect.x, ps.floor_offset['y'] + ps.base_rect.y)
    ps.floor_rect.topleft = ps.floor_location
    screen.blit(ps.floor_image, ps.floor_rect)
    tile_rect = Rect(0, 0, 35, 35)
    for tile in ps.tiles:
         tile_rect.topleft = tuple(map(sum,zip(tile, ps.floor_location, ps.tiles_offset)))
         screen.fill(FLOOR, tile_rect)
         
         #draw.rect not HW accelerated?  Might be punishing rpi.
         draw.rect(screen, TILEBORDER, tile_rect,  1)
         
    
    
    for k, room in ps.rooms.items():
        room['location'] = tuple(map(sum,zip((room['x_pix'], room['y_pix']),ps.floor_location, ps.tiles_offset)))
        
        room['rect'].topleft = room['location']
        
        for key, v in room.items():
            if key == 'image':
                try:
                    room['imagerect'].topleft = room['rect'].topleft
                    screen.blit(room['roomimage'], room['imagerect'])
                except(KeyError):
                    pass
                    #print('image not found: ' + room['image'])
                break
        
        for key, v in room.items():
            if key == 'system':
                room['system_image_rect'].center = room['rect'].center
                screen.blit(room['system_image'], room['system_image_rect']) #These should be masks
                break
        draw.rect(screen, BLACK, room['rect'],  3)
            #room0_x = room0_x + ps_floor_location[0]
            #room0_y = room0_y + ps_floor_location[1]
        #for crew_member in ps.crew:
        #    blitCrewMember(crew_member, ps, de, screen)
    
    

    #screen.blit(images['s_pilot_overlay'], room0_loc)
    
    
def play():    
        
    screen_x = 1280
    screen_y = 720
    screen_center = (screen_x / 2, screen_y / 2)
    
    
    #enable framebuffer on Raspi.  Might break on non-linux stuff.
    disp_no = os.getenv("DISPLAY")
    if disp_no:
        print("I'm running under X display = " + str(disp_no))
        screen = pygame.display.set_mode((screen_x, screen_y))     
    else:
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print ('Driver: ' + driver + ' failed')
                continue
            found = True
            break

        if not found:
            raise Exception('No suitable video driver found!')
        screen = pygame.display.set_mode((screen_x, screen_y), pygame.FULLSCREEN)
    screen.fill(BLACK)
    
    
    title_background = pygame.image.load('layouts/main_menu_background.png').convert()
    screen.blit(title_background, screen.get_rect())
    pygame.display.flip()
    
    clock = pygame.time.Clock()
    
    de = DataEngine()
    de.newGame('easy', 'default')
    
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mixer.init()
    pygame.font.init()
        
    k_up = k_down = k_left = k_right = 0
    
    #load images 
    #partytime
    images = {}
    print('Loading images...')
    #for image_file, image_path in de.gamepack['img'].items():
    #    print('\t'+image_file)
    #    if image_file != 'path':
    #        images[image_file] = pygame.image.load(str(image_path)).convert_alpha()
    
    #de.images = images #Just for Debugging.  de shouldn't need this.
    #map_background = images['zone_1']
    pygame.mouse.set_visible(False)
    
    #main menu images
    hangar_background = pygame.image.load(str(de.gamepack['img']['custom_main'])).convert()
    pointer_valid = pygame.image.load(str(de.gamepack['img']['pointerValid'])).convert_alpha()
    pointer_invalid = pygame.image.load(str(de.gamepack['img']['pointerInvalid'])).convert_alpha()
    
    
    #main menu buttons
    buttons = {}
    buttons_top = 285
    counter = 0
    button_suffixes = ['on', 'off', 'select2']
    button_names = ['continue', 'start', 'tutorial', 'stats', 'options', 'credits', 'quit']
    
    for button_name in button_names:
        button = {}
        button['image'] = {}
        for button_suffix in button_suffixes:
            button_image_string = button_name + '_' + button_suffix
            button['image'][button_suffix] =  pygame.image.load(str(de.gamepack['img'][button_image_string])).convert_alpha()
        button['image']['current'] = button['image']['on']
        button['name'] = button_name
        button['rect'] = button['image']['on'].get_rect()
        button['rect'].right = 1190
        button['rect'].top = buttons_top + (counter * 60)
        counter += 1
        buttons[button_name] = button
        
    
    #set up main UI
    ui = {}
    ui['jump_button_charged'] = pygame.image.load(str(de.gamepack['img']['FTL_JUMP'])).convert_alpha()
    ui['map_backgrounds'] = []
    ui['map_backgrounds'].append(pygame.image.load(str(de.gamepack['img']['zone_1'])))
    ui['map_backgrounds'].append(pygame.image.load(str(de.gamepack['img']['zone_2'])))
    ui['map_backgrounds'].append(pygame.image.load(str(de.gamepack['img']['zone_3'])))
    map_background_rect = ui['map_backgrounds'][0].get_rect()
    map_background_rect.center = screen_center
    
    ui['map_images'] = {}
    ui['map_images']['unvisited'] = pygame.image.load(str(de.gamepack['img']['map_icon_diamond_yellow'])).convert_alpha()
    beacon_rect = ui['map_images']['unvisited'].get_rect()
    ui['map_images']['visited'] = pygame.image.load(str(de.gamepack['img']['map_icon_diamond_blue'])).convert_alpha()
    ui['map_images']['warning'] = pygame.image.load(str(de.gamepack['img']['map_icon_warning'])).convert_alpha()
    ui['map_images']['danger'] = pygame.image.load(str(de.gamepack['img']['map_icon_triangle_red'])).convert_alpha()
    ui['map_images']['ship'] = pygame.image.load(str(de.gamepack['img']['map_icon_ship'])).convert_alpha()    
    ui['map_images']['targetbox'] = pygame.image.load(str(de.gamepack['img']['map_targetbox'])).convert_alpha()
    
    #We don't need alpha for these.  They are always the bottom layer
    backgrounds = { 'blueStarcluster': pygame.image.load(str(de.gamepack['img']['bg_blueStarcluster'])).convert(),
                    'darknebula':  pygame.image.load(str(de.gamepack['img']['bg_darknebula'])).convert(),
                    'dullstars': pygame.image.load(str(de.gamepack['img']['bg_dullstars'])).convert(),
                    'dullstars2': pygame.image.load(str(de.gamepack['img']['bg_dullstars2'])).convert(),
                    'lonelyRedStar': pygame.image.load(str(de.gamepack['img']['bg_lonelyRedStar'])).convert(),
                    'lonelyStar': pygame.image.load(str(de.gamepack['img']['bg_lonelystar'])).convert()
                   }
    background = backgrounds['lonelyStar']
    planets = {'bigblue': pygame.image.load(str(de.gamepack['img']['planet_bigblue'])).convert_alpha(),
               'brown': pygame.image.load(str(de.gamepack['img']['planet_brown'])).convert_alpha(),
               'gas_blue': pygame.image.load(str(de.gamepack['img']['planet_gas_blue'])).convert_alpha(),
               'gas_yellow': pygame.image.load(str(de.gamepack['img']['planet_gas_yellow'])).convert_alpha(),
               'peach': pygame.image.load(str(de.gamepack['img']['planet_peach'])).convert_alpha(),
               'populated_brown': pygame.image.load(str(de.gamepack['img']['planet_populated_brown'])).convert_alpha(),
               'populated_dark': pygame.image.load(str(de.gamepack['img']['planet_populated_dark'])).convert_alpha(),
               'populated_orange': pygame.image.load(str(de.gamepack['img']['planet_populated_orange'])).convert_alpha(),
               'red': pygame.image.load(str(de.gamepack['img']['planet_red'])).convert_alpha(),
               'sun1': pygame.image.load(str(de.gamepack['img']['planet_sun1'])).convert_alpha()
               }
    populated = []
    populated.append(planets['populated_brown'])
    populated.append(planets['populated_dark'])
    populated.append(planets['populated_orange'])
    
    
    #set up fonts
    pygame.font.init()
    font_10 = pygame.font.Font(str(de.gamepack['fonts']['JustinFont10']), 10)
    font_11 = pygame.font.Font(str(de.gamepack['fonts']['JustinFont11']), 11)
    font_11_bold = pygame.font.Font(str(de.gamepack['fonts']['JustinFont11Bold']), 11)
    font_12 = pygame.font.Font(str(de.gamepack['fonts']['JustinFont12']), 12)
    font_12_bold = pygame.font.Font(str(de.gamepack['fonts']['JustinFont12Bold']), 14)
    font_7 = pygame.font.Font(str(de.gamepack['fonts']['JustinFont7']), 7)
    font_8 = pygame.font.Font(str(de.gamepack['fonts']['JustinFont8']), 8)
    num_font =pygame.font.Font(str(de.gamepack['fonts']['num_font']), 10)
    cc_font = pygame.font.Font(str(de.gamepack['fonts']['c&c']), 14)
    cc_new_font = pygame.font.Font(str(de.gamepack['fonts']['c&cnew']), 14)
    
    choice_rects = []
    
    
    
    
    #load sounds
    
    #Can't preload sounds and have it still work on pi.
    #print('Loading sounds ...')
    
    #sounds = {}
    #for sound_file, sound_path in de.gamepack['sounds'].items():
    #    print('\t'+sound_file)
    #    if sound_file != 'path':
    #        sounds[sound_file] = pygame.mixer.Sound(str(sound_path))
            
    #print('Loading Music...')
    #loading all these sounds in advance chews up fucktons of RAM
    #music = {}
    
    #DO THIS SOMEWHERE ELSE! (Really, this is a job for the Clonebay_Importer): Sanitize stuff
    # Inconsistencies make this tough!
    mpre = 'bp_MUS_'
    track_map = {'civilian': 'Civil',
                 'colonial': 'Colonial',
                 'cosmos': 'Cosmos',
                 'debris': 'Debris',
                 'deepspace': 'Deepspace',
                 'engi': 'Engi',
                 'hack': 'Hack',
                 'lostship': 'LostShip',
                 'mantis': 'Mantis',
                 'milkyway': 'MilkyWay',
                 'rockmen': 'Rockmen',
                 'shrike': 'Shrike',
                 'slug': 'Slug',
                 'void': 'Void',
                 'wasteland': 'Wasteland',
                 'zoltan': 'Zoltan'                 
                 }
    print(track_map)
    for key, value in track_map.items():
        track_map[key] = mpre + value
    
    #for music_file, music_path in de.gamepack['music'].items():
        #print('\t'+music_file)
        #if music_file != 'path':
            #music[music_file] = pygame.mixer.Sound(str(music_path))
    
    
    
    bleep = pygame.mixer.Sound(str(de.gamepack['sounds']['select_light1']))
    music_vol = 0.05
    game_vol = 1.0
    current_vol = 0.000
    
    #initialize the game state
    
    flippers = False
    countie = 0
    indy = 0
    paused = True
    in_combat = False
    jump_ready = True
    first_time = True
    can_continue = False
    mouse_image = pointer_invalid
    game_view = 'main_menu' 
    bleeping = False
    pressing_key = False
    show_game_menu = False

    player_ships = []
    player_ship_index = 0
    for shipBlueprint in de.shipBlueprints:
        if 'PLAYER_SHIP' in shipBlueprint['@name']:
            player_ships.append(shipBlueprint)
            print(shipBlueprint['name'])
    player_ships_count = len(player_ships) - 1
    de.player_ship = Ship(player_ships[0], de)
    initPlayerShip(de.player_ship, de)
    
    
    
    # game
    
    subview = 'none'
    visited_beacons = []
        
    
    #Main Game loop
    while 1:
        # USER INPUT
        clock.tick(60)
        screen.fill(BLACK)
        mousepos = pygame.mouse.get_pos()
        if game_view == 'main_menu':
            for event in pygame.event.get():
                if not hasattr(event, 'key'): continue
                down = event.type == KEYDOWN
                pass   
            #stuff to do first time:
            if first_time:
                #play music
                title_music = pygame.mixer.Sound(str(de.gamepack['music']['bp_MUS_TitleScreen']))
                title_music.set_volume(music_vol)
                title_music.play(-1)
                first_time = False
    
            
            #blit the background
    
            screen.blit(title_background, screen.get_rect())
            mousepos = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed()
            hovered = False
            for k, button in buttons.items():
                if button['rect'].collidepoint(mousepos):
                    button['image']['current'] = button['image']['select2']
                    mouse_image = pointer_valid
                    hovered = True
                    if mouse_buttons[0]:
                        if button['name'] == 'quit': 
                            sys.exit(0)
                        elif button['name'] == 'start':
                            game_view = 'hangar'
                    
                    
                else:
                    button['image']['current'] = button['image']['on']
                    mouse_image = pointer_invalid
                #button_images.append(button['image']['on'])
                #button_rects.append(button['rect'])
    
                screen.blit(button['image']['current'], button['rect'])
            if hovered:
                if not bleeping:
                    bleep.play()
                bleeping = True
            else:
                bleeping = False
            
            #blit the planet
            
            #blit the ships
            
            #blit Game title
            
            #blit Menu items
            
            #set the music
            #handle inputs
            
        
    
        elif game_view == 'main_options':
            pass
    
        elif game_view == 'main_stats':
            pass
        
        elif game_view == 'hangar':
            #handle inputs
            for event in pygame.event.get():
                if not hasattr(event, 'key'): continue
                down = event.type == KEYDOWN
                if not down: pressing_key = False
                    #KEY DOWN OR UP?
                if event.key == K_ESCAPE: 
                    game_view = 'main_menu'
                elif event.key == K_RETURN:
                    game_view = 'game'
                    first_time = True
                    screen.blit(title_background, screen.get_rect())
                    pygame.display.flip() 
                elif event.key == K_UP and down:
                    if not pressing_key:
                        if player_ship_index == player_ships_count:
                            player_ship_index = 0                    
                        else: 
                            player_ship_index += 1
                        de.player_ship = Ship(player_ships[player_ship_index], de)
                        initPlayerShip(de.player_ship, de)
                        print("Ship selected: " + de.player_ship.id + " -- "+ de.player_ship.name)
                    pressing_key = True
                elif event.key == K_DOWN and down:
                    if not pressing_key:    
                        if player_ship_index == 0:
                            player_ship_index = player_ships_count
                        else: 
                            player_ship_index -= 1
                        de.player_ship = Ship(player_ships[player_ship_index], de)
                        initPlayerShip(de.player_ship, de)
                        print("Ship selected: " + de.player_ship.id + " -- "+ de.player_ship.name)
                    pressing_key = True
            
    
            screen.blit(hangar_background, screen.get_rect())
            blitPlayerShip(de.player_ship, (640, 210), screen, de)
            
            
            
        if game_view == 'game':
            
            #This needs to happen early, or stuff won't work.
             #Store these for different handling based on context.
            

            if first_time:
                #get the starting event
                cur_sector = de.world_map[0]
                cur_beacon = cur_sector['beacons'][0]
                cur_beacon['background'] = background
                cur_event = cur_beacon['event']
                visited_beacons.append(cur_beacon['id'])
                subview = 'show_event'
                first_time = False
                #set up the music
                title_music.stop()
                avl_tracks = cur_sector['description']['trackList']['track']
                randomizer = randint(0, len(avl_tracks) - 1)
                trackset = avl_tracks[randomizer]
                randomizer = randint(0, len(ui['map_backgrounds']) - 1)
                map_background = ui['map_backgrounds'][randomizer]
                
                #Need to clean this stuff up in dataloader
                
                mus_explore =  pygame.mixer.Sound(str(de.gamepack['music'][track_map[trackset]+'EXPLORE']))
                mus_battle =   pygame.mixer.Sound(str(de.gamepack['music'][track_map[trackset]+'BATTLE']))
                mus_explore.set_volume(music_vol)
                mus_explore.set_volume(0)
                mus_explore.play(-1)
                mus_battle.play(-1)
                #map_background = pygame.image.load()
                randomizer = randint(0, len(planets) - 1)
                i = 0
                for k, planet in planets.items():
                    if i == randomizer:
                        cur_beacon['planet'] = planet
                        cur_beacon['planet_rect'] = planet.get_rect()
                        cur_beacon['planet_rect'].center = (randint (0, screen_x), randint(0, screen_y))
                        break
                    i += 1
                    
                
            
            frame_events = pygame.event.get()
            mouse_buttons = pygame.mouse.get_pressed()
            # do input handling that should happen consistently every frame, such as 'KEY_ESC'.
            
            
            #de.tick(paused)
            
            #BLITTING ORDER: (FROM BOTTOM TO TOP)
            #    background 
            #        background image
            #        background planets
            #    
            #    player ship (Location depends if in_combat)
            #            
            #    if in combat
            #        enemy ship
            #    
            #    projectiles
            #    
            #    
            #    Main UI Stuffs
            #
            #    subviews:
            #        'esc' menu
            #        'beacon_map'
            #        'show_event'
            #        'upgrades'
            #        'crew'
            #        'equipment'
            #        'store'
            #
            #    Menus
            
    
            
            #draw the background
            screen.fill(BLACK)

            screen.blit(cur_beacon['background'], screen.get_rect())
            screen.blit(cur_beacon['planet'], cur_beacon['planet_rect'])
           
            try:
                if 'text' in cur_event.items():
                    if '@planet' in cur_event['text'].items():
                        pass
            except(KeyError):
                pass
            except(AttributeError):
                pass
            except(ValueError):
                pass
            except(TypeError):
                pass
            
            
            #do more here
            
            
            
            #Draw ships
            if not in_combat:
                position = screen_center
                blitPlayerShip(de.player_ship, position, screen, de)
                
            else:
                position = screen_center #just for now,  figure out the offsets later.
                blitPlayerShip(de.player_ship, position, screen, de)
                #blitEnemyShip()
                #blitProjectiles()
                #
                
                #pass 
            #blit systems and crew UI
            
            #just for testing
            if jump_ready:
                jump_ready_rect = ui['jump_button_charged'].get_rect()
                jump_ready_rect.x = 500
                screen.blit(ui['jump_button_charged'], jump_ready_rect)
                
            
            if subview == 'none':
                if jump_ready_rect.collidepoint(mousepos):
                    if mouse_buttons[0]:
                        subview = 'beacon_map'
                #handle inputs for combat, or idling
                #everything should already be drawn.
           

            elif subview == 'show_event':
                choice_rects = []
                paused = True
                
                event_rect = Rect(400, 300, 400, 300)
                event_rect.center = screen_center
                
                #blit the event window
                
                
                #blit the text
                #drawText(surface, text, color, rect, font, aa, bkg)
                screen.fill(BLACK, event_rect)
                event_rect.h -= 20
                event_rect.w -= 20
                event_rect.x += 10
                event_rect.y += 10
                try:
                    full, offset = drawText(screen, cur_event['text'], WHITE, event_rect, font_12_bold, bkg=BLACK )
                except(TypeError):
                    try:
                        full, offset = drawText(screen, cur_event['text']['#text'], WHITE, event_rect, font_12_bold, bkg=BLACK )
                    except(TypeError):
                        print("D'oh!")
                except(KeyError):
                    print("ERROR!  THIS EVENT HAS NO 'text'")
                    print(cur_event)
                    cur_event['text'] = 'ERROR!'
                event_rect.h -= 20
                event_rect.w -= 20
                event_rect.x += 10
                event_rect.y += 10

                #blit the choices
                i = 0
                if 'choices' in cur_event:
                    choices = cur_event['choices']                    
                    for choice in choices:
                        choice_rects.append(event_rect)
                        choice_rects[i].top = offset + 10
                        if '#text' in choice['text']:
                            choice_text = choice['text']['#text']
                        else:
                            choice_text = choice['text']
                        full, offset = drawText(screen, str(i+1) + '. ' + choice_text, WHITE, choice_rects[i], font_12_bold) 
                        choice_rects[i].h = offset - choice_rects[i].top 
                        
                        if choice_rects[i].collidepoint(mousepos):
                            full, choicebottom = drawText(screen, str(i+1) + '. ' + choice_text, YELLOW, choice_rects[i], font_12_bold)
                            if mouse_buttons[0]:
                                
                                try:
                                    tmp_event = choice['event']
                                    for k, v in tmp_event.items():
                                        if k == '@load':
                                            cur_event = de.find_event(v)
                                            break
                                    else:
                                        cur_event = tmp_event
                                except(AttributeError):
                                    subview = 'none'  
                        offset += 10
                        i += 1
                    else:
                        choice_rects.append(event_rect)
                        choice_rects[i].top = offset + 10
                        full, choicebottom = drawText(screen, '1. Ok', WHITE, choice_rects[i], font_12_bold) 
                        choice_rects[i].h =  choicebottom - choice_rects[i].top 
                        if choice_rects[i].collidepoint(mousepos):
                            full, choicebottom = drawText(screen, '1. Ok', YELLOW, choice_rects[i], font_12_bold) 
                            if mouse_buttons[0]:
                                subview = 'none'
                else:
                    choice_rects.append(event_rect)
                    choice_rects[i].top = offset + 10
                    full, choicebottom = drawText(screen, '1. Ok', WHITE, choice_rects[i], font_12_bold) 
                    choice_rects[i].h =  choicebottom - choice_rects[i].top 
                    if choice_rects[i].collidepoint(mousepos):
                        full, choicebottom = drawText(screen, '1. Ok', YELLOW, choice_rects[i], font_12_bold) 
                        if mouse_buttons[0]:
                            subview = 'none'
                    



                #for choice in event_cur['choices']:
                #    pass
                
                
                #blit systems, crew UI
                
                #input handling
                
                #process the outcome
                

                
            
            
            
            elif subview == 'beacon_map':    
                
                screen.blit(map_background, map_background_rect)
                for beacon in cur_sector['beacons']:
                    beacon_x = beacon['x'] + 300
                    beacon_y = beacon['y'] + 165
                    if beacon['id'] == cur_beacon['id']:
                        beacon_image = ui['map_images']['ship']
                    elif beacon['id'] in visited_beacons:
                        beacon_image = ui['map_images']['visited']
                    else:
                        beacon_image = ui['map_images']['unvisited']
                    if beacon['id'] in cur_beacon['connections']:
                        #show connections
                        pass                        

                    beacon_location = (beacon_x, beacon_y)
                    beacon_rect.center =beacon_location
                    screen.blit(beacon_image, beacon_rect)
                    if beacon_rect.collidepoint(mousepos):
                        
                        if beacon['id'] in cur_beacon['connections']:
                            screen.blit(ui['map_images']['targetbox'], beacon_rect)
                            
                            #play bleeping sound
                            if mouse_buttons[0]:
                                #Jump!
                                
                                #animate the jump!
                                
                                cur_beacon = beacon
                                cur_event = cur_beacon['event']
                                subview = 'show_event'
                                i = 0
                                visited_beacons.append(cur_beacon['id'])
                                for k, v in cur_beacon.items():
                                    if k == 'background':
                                        break
                                else:
                                    randomizer = randint(0, len(backgrounds)-1)
                                    for k, background in backgrounds.items():
                                        if i == randomizer:
                                            cur_beacon['background'] = background
                                            break
                                        i += 1
                                    i = 0
                                
                                for k, v in cur_beacon.items():
                                    if k == 'planet':
                                        break
                                else:    
                                    i = 0
                                    randomizer = randint(0, len(planets)-1)
                                    for k, planet in planets.items():
                                        if i == randomizer:
                                            cur_beacon['planet'] = planet
                                            cur_beacon['planet_rect'] = planet.get_rect()
                                            cur_beacon['planet_rect'].center = (randint (0, screen_x), randint(0, screen_y))
                                            break
                                        i += 1
                                
                        else:
                            #show beacon connections
                            pass
                        
            
            
            elif subview == 'sector_map':
                #handle inputs
                pass
            
            
    
            
            elif subview == 'upgrades':
                #handle inputs
                pass
            
            elif subview == 'equipment':
                #handle inputs
                pass
            
            elif subview == 'crew':
                #handle inputs
                pass
            
            elif subview == 'store':
                pass
            
            #blit ship stats ui (Shields, scrap, hull, etc...)
            #This stuff is not interactive
            
            
            
            if show_game_menu:
                #handle inputs
                pass
            
            
            
            
            
            
            
            #de.tickPost()
                
        screen.blit(mouse_image, mousepos)
        pygame.display.flip()    
            #if not flippers:
            #    sound_battle.set_volume(current_vol)
            #    sound_explore.set_volume(1.000 - current_vol)
            #    current_vol += .01
            #    if current_vol >= 1.0:
            #        flippers = True
            #        current_vol = 0.000
            #else:
            #    sound_explore.set_volume(current_vol)
            #    sound_battle.set_volume(1.000 - current_vol)
            #    current_vol += .01
            #    if current_vol >= 1.0:
            #        flippers = False
            #        current_vol = 0.000
    return 0
gamestatus = play()