# -*- coding: utf-8 -*-
# *  Credits:
# *
# *  original Audio Profiles code by Regss
# *  updates and additions through v1.4.1 by notoco and CtrlGy
# *  updates and additions since v1.4.2 by pkscout

import json, os, sys
from kodi_six import xbmc, xbmcgui
from resources.lib import dialog
from resources.lib.fileops import *
from resources.lib.xlogger import Logger
from resources.lib.kodisettings import *

SNAME = {
    1: getSettingString( 'name1' ),
    2: getSettingString( 'name2' ),
    3: getSettingString( 'name3' ),
    4: getSettingString( 'name4' )
}
SPROFILE = {
    1: getSettingBool( 'profile1' ),
    2: getSettingBool( 'profile2' ),
    3: getSettingBool( 'profile3' ),
    4: getSettingBool( 'profile4' )
}
LOGDEBUG     = getSettingBool( 'debug' )
LW           = Logger( preamble='[Audio Profiles]', logdebug=LOGDEBUG )
CECCOMMANDS  = ['', 'CECActivateSource', 'CECStandby', 'CECToggleState']
KODIPLAYER   = xbmc.Player()
DIALOG       = xbmcgui.Dialog()

def convert( data ):
    if sys.version_info < (3, 0):    return data
    if isinstance(data, bytes):      return data.decode()
    if isinstance(data, (str, int)): return str(data)
    if isinstance(data, dict):       return dict(list(map(convert, list(data.items()))))
    if isinstance(data, tuple):      return tuple(map(convert, data))
    if isinstance(data, list):       return list(map(convert, data))
    if isinstance(data, set):        return set(map(convert, data))



class PROFILES:

    def __init__( self ):
        LW.log( ['script version %s started' % ADDONVERSION], xbmc.LOGINFO )
        LW.log( ['debug logging set to %s' % LOGDEBUG], xbmc.LOGINFO )
        LW.log( ['SYS.ARGV: %s' % str(sys.argv)] )
        self.XMLFILE = 'script-audio-profiles-menu.xml'
        self.NOTIFYTIME = getSettingInt( 'notify_time', default=5 ) * 1000
        self.DISPLAYNOTIFICATION = getSettingBool( 'notify', default=True )
        success, loglines = checkPath( os.path.join( ADDONDATAPATH, '' ) )
        LW.log( loglines )
        if (len(sys.argv) < 2 or len(sys.argv[0]) == 0):
            mode = False
        else:
            args = sys.argv[1].split( '&' )
            mode = args[0]
            self.FROMMONITOR = False
            try:
                if args[1] == 'auto':
                    self.FROMMONITOR = True
            except IndexError:
                self.FROMMONITOR = False
        LW.log( ['MODE: %s' % str(mode)] )
        self.start( mode )
        LW.log( ['script version %s stopped' % ADDONVERSION], xbmc.LOGINFO )


    def start( self, mode ):
        if True not in SPROFILE.values():
            self.notification( ADDONLANGUAGE(32105), getSettingBool( 'notify_maintenance', default=True ) )
            ADDON.openSettings()
        if mode is False:
            self.save()
            return
        if mode == 'popup':
            enabledProfiles = self.getEnabledProfiles()
            force_dialog = not KODIPLAYER.isPlaying()
            ret, loglines = dialog.DIALOG().start( self.XMLFILE, labels={10071: ADDONLANGUAGE(32106)}, buttons=enabledProfiles[1],
                                        thelist=10070, force_dialog=force_dialog )
            LW.log( loglines )
            if ret is not None:
                self.profile( str( enabledProfiles[0][ret] ) )
            return
        if mode == '0' or mode == '1' or mode == '2' or mode == '3' or mode == '4':
            if self.check( mode ) is False:
                return
            if mode == '0':
                self.toggle( mode )
            else:
                self.profile( mode )
            return
        LW.log( ['Wrong arg, use like RunScript("%s,x") x - number of profile' % ADDONNAME], xbmc.LOGERROR )


    def getEnabledProfiles( self ):
        enabledProfileKey = []
        enabledProfileName = []
        for k, p in SPROFILE.items():
            if p:
                enabledProfileKey.append( k )
                enabledProfileName.append( SNAME[k] )
        return [enabledProfileKey, enabledProfileName]


    def save( self ):
        enabledProfiles = self.getEnabledProfiles()
        ret, loglines = dialog.DIALOG().start( self.XMLFILE, labels={10071: ADDONLANGUAGE(32100)}, buttons=enabledProfiles[1],
                                    thelist=10070, force_dialog=True )
        LW.log( loglines )
        LW.log( [ 'the returned value is %s' % str(ret) ] )
        if ret is None:
            return False
        else:
            button = enabledProfiles[0][ret]
        settingsToSave = {}
        json_s = [
            '{"jsonrpc":"2.0","method":"Settings.GetSettings", "params":{"level": "expert", "filter":{"section":"system","category":"audio"}},"id":1}',
            '{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["volume"]}, "id": 1}',
            '{"jsonrpc":"2.0","method":"Settings.GetSettings", "params":{"level": "expert", "filter":{"section":"player","category":"videoplayer"}}, "id":1}',
            '{"jsonrpc":"2.0","method":"Settings.GetSettings", "params":{"level": "expert", "filter":{"section":"system","category":"display"}}, "id":1}'
                 ]
        for j in json_s:
            jsonGet = xbmc.executeJSONRPC( j )
            jsonGet = json.loads( jsonGet )
            LW.log( ['JSON: %s' % str( jsonGet )] )
            if 'result' in jsonGet:
                if 'settings' in jsonGet['result']:
                    for theset in jsonGet['result']['settings']:
                        if 'value' in theset.keys():

                            if theset['value'] == True or theset['value'] == False:
                                settingsToSave[theset['id']] = str(theset['value']).lower()
                            else:
                                if isinstance(theset['value'],int):
                                    settingsToSave[theset['id']] = str(theset['value'])
                                else:
                                    settingsToSave[theset['id']] = str(theset['value']).encode( 'utf-8' )

                if 'volume' in jsonGet['result']:
                    settingsToSave['volume'] = str( jsonGet['result']['volume'] )
        jsonToWrite = json.dumps( convert( settingsToSave ) )
        LW.log( ['[SAVING SETTING]: %s' % SNAME[button]], xbmc.LOGINFO )
        success, loglines = writeFile( jsonToWrite, os.path.join( ADDONDATAPATH, 'profile%s.json' % str( button ) ), 'w' )
        LW.log( loglines )
        if success:
            self.notification( '%s %s (%s)' % (ADDONLANGUAGE(32102), str(button), SNAME[button]), getSettingBool( 'notify_maintenance', default=True ) )


    def check( self, mode ):
        self.aProfile = []
        if mode != '0' and not SPROFILE[int( mode )]:
            self.notification( '%s (%s)' % (ADDONLANGUAGE(32103), SNAME[int(mode)]), getSettingBool( 'notify_maintenance', default=True ) )
            LW.log( ['[CHECK]: This profile is disabled in addon settings - %s' % str(mode)], xbmc.LOGINFO )
            return False
        for key in SPROFILE:
            if SPROFILE[key]:
                success, loglines = checkPath( os.path.join( ADDONDATAPATH, 'profile%s.json' % str( key ) ), createdir=False )
                LW.log( loglines )
                if not success:
                    self.notification( '%s %s (%s)' % (ADDONLANGUAGE( 32101 ), str( key ), SNAME[key]), getSettingBool( 'notify_maintenance', default=True ) )
                    LW.log( ['[PROFILE FILE]: not exist for profile - %s' % str(key)], xbmc.LOGERROR )
                    return False
                self.aProfile.append( str( key ) )


    def toggle( self, mode ):
        loglines, profile = readFile( os.path.join( ADDONDATAPATH,'profile' ) )
        LW.log( loglines )
        if profile:
            if (len( self.aProfile ) == 1) or (profile not in self.aProfile):
                profile = self.aProfile[0]
            else:
                ip = int( self.aProfile.index(profile) )
                if len( self.aProfile ) == ip:
                    try:
                        profile = self.aProfile[0]
                    except IndexError:
                        profile = self.aProfile[0]
                else:
                    try:
                        profile = self.aProfile[ip + 1]
                    except IndexError:
                        profile = self.aProfile[0]
        else:
            profile = self.aProfile[0]
        self.profile( profile )


    def profile(self, profile):
        loglines, result = readFile( os.path.join( ADDONDATAPATH, 'profile%s.json' % profile ) )
        LW.log( loglines )
        try:
            jsonResult = json.loads( result )
        except ValueError:
            self.notification( '%s %s (%s)' % (ADDONLANGUAGE( 32104 ), profile, SNAME[int( profile )]), getSettingBool( 'notify_maintenance' ), default=True )
            LW.log( ['LOAD JSON FROM FILE: Error reading from profile - %s' % str( profile )], xbmc.LOGERROR )
            return False
        quote_needed = ['audiooutput.audiodevice',
                        'audiooutput.passthroughdevice',
                        'locale.audiolanguage',
                        'lookandfeel.soundskin']
        LW.log( ['[RESTORING SETTING]: %s' % SNAME[int( profile )]], xbmc.LOGINFO )
        for setName, setValue in jsonResult.items():
            if not getSettingBool( 'player' ) and setName.startswith('videoplayer'):
                continue
            if not getSettingBool( 'video' ) and setName.startswith('videoscreen'):
                continue
            LW.log( ['[RESTORING SETTING]: %s: %s' % (setName,setValue)] )
            if setName in quote_needed:
                setValue = '"%s"' % setValue
            if getSettingBool( 'volume' ) and setName == 'volume':
                xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "Application.SetVolume", "params": {"volume": %s}, "id": 1}' % jsonResult['volume'] )
            else:
                xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "Settings.SetSettingValue", "params": {"setting": "%s", "value": %s}, "id": 1}' % (setName, setValue) )
        if self.FROMMONITOR:
            show_notification = getSettingBool( 'notify_auto', default=True )
        else:
            show_notification = getSettingBool( 'notify_manual', default=True )
        self.notification( SNAME[int( profile )], show_notification )
        success, loglines = writeFile( profile, os.path.join(ADDONDATAPATH, 'profile'), 'w' )
        LW.log( loglines )
        sCec = getSettingInt('profile%s_cec' % profile )
        if sCec:
            LW.log( ['[SENDING CEC COMMAND]: %s' % CECCOMMANDS[sCec]], xbmc.LOGINFO )
            xbmc.executebuiltin(CECCOMMANDS[sCec])


    def notification( self, msg, display=True):
        if self.DISPLAYNOTIFICATION and display:
            DIALOG.notification( ADDONLONGNAME, msg, icon=ADDONICON, time=self.NOTIFYTIME )
