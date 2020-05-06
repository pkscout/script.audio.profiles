
import os
from resources.lib.fileops import checkPath
from resources.lib.kodisettings import *

SETTINGSLIST = [ 
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
                 {'name': 'profile5', 'default': False},
                 {'name': 'name5', 'default': 'Other'},
                 {'name': 'profile5_cec', 'default': 0},
                 {'name': 'profile6', 'default': False},
                 {'name': 'name6', 'default': 'Other'},
                 {'name': 'profile6_cec', 'default': 0},
                 {'name': 'profile7', 'default': False},
                 {'name': 'name7', 'default': 'Other'},
                 {'name': 'profile7_cec', 'default': 0},
                 {'name': 'profile8', 'default': False},
                 {'name': 'name8', 'default': 'Other'},
                 {'name': 'profile8_cec', 'default': 0},
                 {'name': 'profile9', 'default': False},
                 {'name': 'name9', 'default': 'Other'},
                 {'name': 'profile9_cec', 'default': 0},
                 {'name': 'profile10', 'default': False},
                 {'name': 'name10', 'default': 'Other'},
                 {'name': 'profile10_cec', 'default': 0},
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
                 {'name': 'auto_ac3', 'default': '0'},
                 {'name': 'auto_eac3', 'default': '0'},
                 {'name': 'auto_dts', 'default': '0'},
                 {'name': 'auto_dtshd', 'default': '0'},
                 {'name': 'auto_truehd', 'default': '0'},
                 {'name': 'auto_othercodec', 'default': '0'},
                 {'name': 'auto_stereo', 'default': '0'},
                 {'name': 'auto_multichannel', 'default': '0'},
                 {'name': 'volume', 'default': False},
                 {'name': 'player', 'default': False},
                 {'name': 'video', 'default': False},
                 {'name': 'player_show', 'default': False},
                 {'name': 'auto_default', 'default': '0'},
                 {'name': 'force_auto_default', 'default': False},
                 {'name': 'use_custom_skin_menu', 'default': True},
                 {'name': 'match_custom_to_skin', 'default': True},
                 {'name': 'player_autoclose', 'default': False},
                 {'name': 'player_autoclose_delay', 'default': 10},
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
    settings['SKINNAME'] = _get_skin( settings )
    return settings


def _get_skin( settings ):
    skin = 'Default'
    if not (settings['use_custom_skin_menu'] and settings['match_custom_to_skin']):
        return skin
    skin_glue = 2
    keep_trying = True
    skin_parts = SKINNAME.split('.')
    while keep_trying:
        skin_test = '.'.join( skin_parts[:skin_glue] )
        success, loglines = checkPath( os.path.join( ADDONPATH, 'resources', 'skins', skin_test, '' ), createdir=False )
        if success:
            skin = skin_test
            keep_trying = False
        skin_glue += 1
        if skin_glue > len( skin_parts ):
            keep_trying = False
    return skin
