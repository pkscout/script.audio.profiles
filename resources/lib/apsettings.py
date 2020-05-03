
from resources.lib.kodisettings import *

SETTINGSLIST = [ {'name': 'volume', 'default': False},
                 {'name': 'player', 'default': False},
                 {'name': 'video', 'default': False},
                 {'name': 'profile1', 'default': True},
                 {'name': 'name1', 'default': 'Digital'},
                 {'name': 'profile1_cec', 'default': 0},
                 {'name': 'profile2', 'default': True},
                 {'name': 'name2', 'default': 'Analog'},
                 {'name': 'profile2_cec', 'default': 0},
                 {'name': 'profile3', 'default': False},
                 {'name': 'name3', 'default': 'Headphones'},
                 {'name': 'profile3_cec', 'default': 0},
                 {'name': 'profile4', 'default': False},
                 {'name': 'name4', 'default': 'HDMI'},
                 {'name': 'profile4_cec', 'default': 0},
                 {'name': 'player_show', 'default': False},
                 {'name': 'player_autoclose', 'default': False},
                 {'name': 'player_autoclose_delay', 'default': 10},
                 {'name': 'auto_default', 'default': '0'},
                 {'name': 'force_auto_default', 'default': False},
                 {'name': 'auto_gui', 'default': '0'},
                 {'name': 'auto_movies', 'default': '0'},
                 {'name': 'auto_videos', 'default': '0'},
                 {'name': 'auto_tvshows', 'default': '0'},
                 {'name': 'auto_pvr_tv', 'default': '0'},
                 {'name': 'auto_gui', 'default': '0'},
                 {'name': 'auto_music', 'default': '0'},
                 {'name': 'auto_musicvideo', 'default': '0'},
                 {'name': 'auto_pvr_radio', 'default': '0'},
                 {'name': 'auto_unknown', 'default': '0'},
                 {'name': 'menu_diffusion', 'default': '90'},
                 {'name': 'notify', 'default': True},
                 {'name': 'notify_time', 'default': 5},
                 {'name': 'notify_auto', 'default': True},
                 {'name': 'notify_manual', 'default': True},
                 {'name': 'notify_maintenance', 'default': True},
                 {'name': 'debug', 'default': False}
               ]


def loadSettings():
    settings = {}
    settings['ADDON'] = ADDON
    settings['ADDONNAME'] = ADDONNAME
    settings['ADDONLONGNAME'] = ADDONLONGNAME
    settings['ADDONVERSION'] = ADDONVERSION
    settings['ADDONPATH'] = ADDONPATH
    settings['ADDONDATAPATH'] = ADDONDATAPATH
    settings['ADDONICON'] = ADDONICON
    settings['ADDONLANGUAGE'] = ADDONLANGUAGE
    for item in SETTINGSLIST:
        if isinstance( item['default'], bool ):
            getset = getSettingBool
        elif isinstance( item['default'], int ):
            getset = getSettingInt
        elif isinstance( item['default'], float ):
            getset = getSettingNumber
        else:
            getset = getSettingString
        settings[item['name']] = getset( item['name'], item['default'] )
    return settings
