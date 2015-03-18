import pygame, math, sys
from pygame.locals import * 
from pygame import Rect
from pygame import draw

from src.dataEngine import DataEngine
from src.Ship import Ship

BLACK = (0,0,0)
WHITE = (255, 255, 255)
FLOOR = (230, 226, 219)
TILEBORDER = (172, 169, 164)

def initPlayerShip(ps, images):
    ps.base_image = images[ps.base_image_name]
    ps.base_rect = ps.base_image.get_rect()
    ps.floor_image = images[ps.floor_image_name]
    ps.floor_rect = ps.floor_image.get_rect()
    ps.tiles_offset = ((ps.floor_rect.w - ps.width) / 2, (ps.floor_rect.h - ps.height)/2)
    for k, room in ps.rooms.items():
        room['rect'] = Rect(room['x_pix'], room['y_pix'], room['w_pix'], room['h_pix'])
        

    

    

def blitPlayerShip(ps, location, screen, images):
    ps.base_rect.center = location
    screen.blit(ps.base_image, ps.base_rect)
    
        
    ps.floor_location = (ps.floor_offset['x'] + ps.base_rect.x, ps.floor_offset['y'] + ps.base_rect.y)
    ps.floor_rect.topleft = ps.floor_location
    screen.blit(ps.floor_image, ps.floor_rect)
    tile_rect = Rect(0, 0, 35, 35)
    for tile in ps.tiles:
         tile_rect.topleft = tuple(map(sum,zip(tile, ps.floor_location, ps.tiles_offset)))
         screen.fill(FLOOR, tile_rect)
         draw.rect(screen, TILEBORDER, tile_rect,  1)
         
    
    
    for k, room in ps.rooms.items():
        room['location'] = tuple(map(sum,zip((room['x_pix'], room['y_pix']),ps.floor_location, ps.tiles_offset)))
        
        room['rect'].topleft = room['location']
        
        for key, v in room.items():
            if key == 'image':
                try:
                    imagerect = images[room['image']].get_rect()
                    imagerect.topleft = room['rect'].topleft
                    screen.blit(images[room['image']], imagerect)
                except(KeyError):
                    print('image not found: ' + room['image'])
        
        for key, v in room.items():
            if key == 'system':
                system_image = images['s_' + room['system']['name'] + '_overlay']
                system_image_rect = system_image.get_rect()
                system_image_rect.center = room['rect'].center
                screen.blit(system_image, system_image_rect)
        draw.rect(screen, BLACK, room['rect'],  3)
            #room0_x = room0_x + ps_floor_location[0]
            #room0_y = room0_y + ps_floor_location[1]
    
    
    

    #screen.blit(images['s_pilot_overlay'], room0_loc)
    
    
def play():    
        
    screen_x = 1280
    screen_y = 720
    screen_center = (screen_x / 2, screen_y / 2)
    
    screen = pygame.display.set_mode((screen_x, screen_y))     
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
    for image_file, image_path in de.gamepack['img'].items():
        print('\t'+image_file)
        if image_file != 'path':
            images[image_file] = pygame.image.load(str(image_path)).convert_alpha()
    
    de.images = images #Just for Debugging.  de shouldn't need this.
    map_background = images['zone_1']
    pygame.mouse.set_visible(False)
    
    #main menu images
    hangar_background = images['custom_main']
    pointer_valid = images['pointerValid']
    pointer_invalid = images['pointerInvalid']
    
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
            button['image'][button_suffix] =  images[button_image_string]
        button['image']['current'] = button['image']['on']
        button['name'] = button_name
        button['rect'] = button['image']['on'].get_rect()
        button['rect'].right = 1190
        button['rect'].top = buttons_top + (counter * 60)
        counter += 1
        buttons[button_name] = button
    
    
    #load sounds
    
    print('Loading sounds ...')
    
    sounds = {}
    for sound_file, sound_path in de.gamepack['sounds'].items():
        print('\t'+sound_file)
        if sound_file != 'path':
            sounds[sound_file] = pygame.mixer.Sound(str(sound_path))
            
    print('Loading Music...')
    #loading all these sounds in advance chews up fucktons of RAM
    music = {}
    #for music_file, music_path in de.gamepack['music'].items():
        #print('\t'+music_file)
        #if music_file != 'path':
            #music[music_file] = pygame.mixer.Sound(str(music_path))
    #initialize the game state
    
    bleep = sounds['select_light1']
    music_vol = 0.1
    
    
    current_vol = 0.000
    flippers = False
    countie = 0
    indy = 0
    paused = True
    in_combat = False
    first_time = True
    can_continue = False
    mouse_image = pointer_invalid
    game_view = 'main_menu' 
    bleeping = False
    pressing_key = False
    # main_menu
    # main_options
    # main_stats
    # hangar
    player_ships = []
    player_ship_index = 0
    for shipBlueprint in de.shipBlueprints:
        if 'PLAYER_SHIP' in shipBlueprint['@name']:
            player_ships.append(shipBlueprint)
            print(shipBlueprint['name'])
    player_ships_count = len(player_ships) - 1
    de.player_ship = Ship(player_ships[0], de)
    initPlayerShip(de.player_ship, images)
    # game
    subview = ''
    # beacon_map
    # sector_map
    # game_menu
    # store
    # ship_menu_upgrades
    # ship_menu_crew
    # ship_menu_equipment
    # none?
    
    
    
    while 1:
        # USER INPUT
        clock.tick(60)
        screen.fill(BLACK)
        mousepos = pygame.mouse.get_pos()
        if game_view == 'main_menu':
            for event in pygame.event.get():
                if not hasattr(event, 'key'): continue
                down = event.type == KEYDOWN
                    #KEY DOWN OR UP?
                if event.key == K_RIGHT: k_right = down * 5
                elif event.key == K_LEFT: k_left = down * 5
                elif event.key == K_UP: k_up = down * 2
                elif event.key == K_DOWN: k_down = down * 2
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
            for event in pygame.event.get():
                if not hasattr(event, 'key'): continue
                down = event.type == KEYDOWN
                if not down: pressing_key = False
                    #KEY DOWN OR UP?
                if event.key == K_ESCAPE: 
                    game_view = 'main_menu'
                elif event.key == K_UP and down:
                    if not pressing_key:
                        if player_ship_index == player_ships_count:
                            player_ship_index = 0                    
                        else: 
                            player_ship_index += 1
                        de.player_ship = Ship(player_ships[player_ship_index], de)
                        initPlayerShip(de.player_ship, images)
                        print("Ship selected: " + de.player_ship.id + " -- "+ de.player_ship.name)
                    pressing_key = True
                elif event.key == K_DOWN and down:
                    if not pressing_key:    
                        if player_ship_index == 0:
                            player_ship_index = player_ships_count
                        else: 
                            player_ship_index -= 1
                        de.player_ship = Ship(player_ships[player_ship_index], de)
                        initPlayerShip(de.player_ship, images)
                        print("Ship selected: " + de.player_ship.id + " -- "+ de.player_ship.name)
                    pressing_key = True
            
    
            screen.blit(hangar_background, screen.get_rect())
            blitPlayerShip(de.player_ship, (640, 210), screen, images)
            
            
            
    
        elif game_view == 'game':
    
            if not paused:
                de.tick()
            for event in pygame.event.get():
                if not hasattr(event, 'key'): continue
                
                   
                    
            
            #BLITTING ORDER: (FROM BOTTOM TO TOP)
            #    background 
            #        background image
            #        background planets
            #
            #    player ship
            #        shield
            #        base
            #        floor
            #        rooms
            #            ???DOORS?
            #            breaches
            #            o2level
            #            fires
            #            systems
            #            people
            #
            #    enemy ship
            #    
            #    projectiles
            #    
            #    effects?
            #    
            #    Main UI Stuffs
            #
            #    Menus
            
            
            
            
            
            
            x, y = position
            
            
            position = screen_center
            
        
    
            
            map_background_rect = map_background.get_rect()
            map_background_rect.center = screen_center
            map_overlay_rect = map_overlay.get_rect()
            map_overlay_rect.center = screen_center
            
            
           
            
            screen.blit(map_background, map_background_rect)
            #screen.blit(map_overlay, map_overlay_rect)
        
            countie += 1
            if countie == 600:
                countie = 0
                indy = indy + 1
                if indy == 7:
                    indy = 0
            
                
            for beacon in de.world_map[indy]['beacons'].items():
                listy = list(beacon)
                print("Blitting Sector: " + str(indy + 1) + ". beacon_id: " + str(listy[1]['id']))
                beacon_x = listy[1]['x'] + 300
                beacon_y = listy[1]['y'] + 165
                beacon_rect = beacon_image.get_rect()
                beacon_location = (beacon_x, beacon_y)
                beacon_rect.center =beacon_location
                screen.blit(beacon_image, beacon_rect)
                
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