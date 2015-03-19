from src.pathlib import Path 
from src.dataLoader import loadGameData



def loadGamepacks():
    gamepacks = {}
    
    game_path = Path('./')
    gamepacks_path = game_path / 'gamepacks'
    print("Looking for gamepacks:")
    for gamepack_path in list(gamepacks_path.glob('*')):
                gamepack_name = gamepack_path.name
                print("\tFound: " + gamepack_name)
                if gamepack_name == 'clonebay': 
                    print("skipping clonebay")
                    pass #just for now
                else:
                    gamepacks[gamepack_name] = {}
                    gamepacks[gamepack_name]['name'] = gamepack_name
                    gamepacks[gamepack_name]['path'] = gamepack_path
    
    print("Loading gamepacks:")
    for k, gamepack in gamepacks.items():
        print(gamepack['name'] + ' contains: ')
        p = gamepack['path']
        for directory in list(p.glob('*')):
            dname = directory.name
            print("\t" + dname)
            gamepack[dname] = {}
            gamepack[dname]['path'] = directory
        if 'audio' in gamepack:
            print('\tScanning audio files:')
            for directory in list(gamepack['audio']['path'].glob('*')):
                if(directory.name) == 'music':
                    gamepack['music'] = {}
                    gamepack['music']['path'] = directory
                    for musfile in list(directory.glob('*')):
                        suf = musfile.suffix 
                        if suf == '.ogg' or suf == '.wav' or suf == '.mp3':
                            print("Found music file: " + musfile.name)
                            gamepack['music'][musfile.stem] = musfile
                elif directory.name == 'waves':
                    gamepack['sounds'] = {}
                    gamepack['sounds']['path'] = directory
                    for soundfile in list(directory.glob('**/*')):
                        suf = soundfile.suffix 
                        if suf == '.ogg' or suf == '.wav' or suf == '.mp3':
                            print('Found sound file: ' + soundfile.name)
                            gamepack['sounds'][soundfile.stem] = soundfile
        if 'data' in gamepack:
            gamepack['data']['gamedata']= loadGameData(gamepack['data']['path'])
        
        if 'fonts' in gamepack:
            print("\tScanning fonts:")
            for font in list(gamepack['fonts']['path'].glob('*')):
                if(font.suffix == '.ttf'): #I DON'T KNOW WHAT TO DO WITH 24.font
                    print("Found font: " + font.name)
                    gamepack['fonts'][font.stem] = font
            
        if 'img' in gamepack:
            print('\tScanning images:')
            for imagefile in list(gamepack['img']['path'].glob('**/*')):
                suf = imagefile.suffix 
                if suf == '.png':
                    print('Found image file: ' + imagefile.name)
                    gamepack['img'][imagefile.stem] = imagefile       
                            
    return gamepacks