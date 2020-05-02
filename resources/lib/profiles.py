# v.0.2.0

import json, os, sys
from kodi_six import xbmc, xbmcgui
from resources.lib import dialog
from resources.lib.fileops import *



class Profiles:

    def __init__( self, settings, lw, auto=False ):
        self.LW = lw
        self.SETTINGS = settings
        self.AUTO = auto
        self.SNAME = { 1: self.SETTINGS['name1'],
                       2: self.SETTINGS['name2'],
                       3: self.SETTINGS['name3'],
                       4: self.SETTINGS['name4'] }
        self.SPROFILE = { 1: self.SETTINGS['profile1'],
                          2: self.SETTINGS['profile2'],
                          3: self.SETTINGS['profile3'],
                          4: self.SETTINGS['profile4'] }
        self.APROFILE = []
        self.CECCOMMANDS = ['', 'CECActivateSource', 'CECStandby', 'CECToggleState']
        self.ENABLEDPROFILES = self._get_enabled_profiles()
        self.KODIPLAYER = xbmc.Player()
        self.DIALOG = xbmcgui.Dialog()
        self.XMLFILE = 'script-audio-profiles-menu.xml'
        self.NOTIFYTIME = self.SETTINGS['notify_time'] * 1000
        self.DISPLAYNOTIFICATION = self.SETTINGS['notify']
        success, loglines = checkPath( os.path.join( self.SETTINGS['ADDONDATAPATH'], '' ) )
        self.LW.log( loglines )


    def changeProfile( self, mode ):
        if True not in self.SPROFILE.values():
            self._notification( self.SETTINGS['ADDONLANGUAGE'](32105), self.SETTINGS['notify_maintenance'] )
            self.SETTINGS['ADDON'].openSettings()
        if mode is False:
            self._save()
            return
        if mode == 'popup':
            force_dialog = not self.KODIPLAYER.isPlaying()
            ret, loglines = dialog.Dialog().start( self.XMLFILE, labels={10071: self.SETTINGS['ADDONLANGUAGE'](32106)}, buttons=self.ENABLEDPROFILES[1],
                                                   thelist=10070, force_dialog=force_dialog )
            self.LW.log( loglines )
            if ret is not None:
                self._profile( str( self.ENABLEDPROFILES[0][ret] ) )
            return ret
        if mode == '0' or mode == '1' or mode == '2' or mode == '3' or mode == '4':
            if self._check( mode ) is False:
                return
            if mode == '0':
                self._toggle( mode )
            else:
                self._profile( mode )
            return
        self.LW.log( ['Wrong arg, use like RunScript("%s,x") x - number of profile' % self.SETTINGS['ADDONNAME']], xbmc.LOGERROR )


    def _check( self, mode ):
        if mode != '0' and not self.SPROFILE[int( mode )]:
            self._notification( '%s (%s)' % (self.SETTINGS['ADDONLANGUAGE'](32103), self.SNAME[int(mode)]), self.SETTINGS['notify_maintenance'] )
            self.LW.log( ['CHECK: This profile is disabled in addon settings - %s' % str(mode)], xbmc.LOGINFO )
            return False
        for key in self.SPROFILE:
            if self.SPROFILE[key]:
                success, loglines = checkPath( os.path.join( self.SETTINGS['ADDONDATAPATH'], 'profile%s.json' % str( key ) ), createdir=False )
                self.LW.log( loglines )
                if not success:
                    self._notification( '%s %s (%s)' % (self.SETTINGS['ADDONLANGUAGE']( 32101 ), str( key ), self.SNAME[key]),
                                       self.SETTINGS['notify_maintenance'] )
                    self.LW.log( ['PROFILE FILE: not exist for profile - %s' % str(key)], xbmc.LOGERROR )
                    return False
                self.APROFILE.append( str( key ) )


    def _convert( self, data ):
        if sys.version_info < (3, 0):    return data
        if isinstance(data, bytes):      return data.decode()
        if isinstance(data, (str, int)): return str(data)
        if isinstance(data, dict):       return dict(list(map(convert, list(data.items()))))
        if isinstance(data, tuple):      return tuple(map(convert, data))
        if isinstance(data, list):       return list(map(convert, data))
        if isinstance(data, set):        return set(map(convert, data))


    def _get_enabled_profiles( self ):
        enabled_profile_key = []
        enabled_profile_name = []
        for k, p in self.SPROFILE.items():
            if p:
                enabled_profile_key.append( k )
                enabled_profile_name.append( self.SNAME[k] )
        return [enabled_profile_key, enabled_profile_name]


    def _notification( self, msg, display=True):
        if self.DISPLAYNOTIFICATION and display:
            self.DIALOG.notification( self.SETTINGS['ADDONLONGNAME'], msg, icon=self.SETTINGS['ADDONICON'], time=self.NOTIFYTIME )


    def _profile(self, profile):
        loglines, result = readFile( os.path.join( self.SETTINGS['ADDONDATAPATH'], 'profile%s.json' % profile ) )
        self.LW.log( loglines )
        try:
            jsonResult = json.loads( result )
        except ValueError:
            self._notification( '%s %s (%s)' % (self.SETTINGS['ADDONLANGUAGE']( 32104 ), profile, self.SNAME[int( profile )]),
                               self.SETTINGS['notify_maintenance'] )
            self.LW.log( ['LOAD JSON FROM FILE: Error reading from profile - %s' % str( profile )], xbmc.LOGERROR )
            return False
        quote_needed = ['audiooutput.audiodevice',
                        'audiooutput.passthroughdevice',
                        'locale.audiolanguage',
                        'lookandfeel.soundskin']
        self.LW.log( ['RESTORING SETTING: %s' % self.SNAME[int( profile )]], xbmc.LOGINFO )
        for setName, setValue in jsonResult.items():
            if not self.SETTINGS['player'] and setName.startswith('videoplayer'):
                continue
            if not self.SETTINGS['video'] and setName.startswith('videoscreen'):
                continue
            self.LW.log( ['RESTORING SETTING: %s: %s' % (setName, setValue)] )
            if setName in quote_needed:
                setValue = '"%s"' % setValue
            if self.SETTINGS['volume'] and setName == 'volume':
                xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "Application.SetVolume", "params": {"volume": %s}, "id": 1}' % jsonResult['volume'] )
            else:
                xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "Settings.SetSettingValue", "params": {"setting": "%s", "value": %s}, "id": 1}' % (setName, setValue) )
        if self.AUTO:
            show_notification = self.SETTINGS['notify_auto']
        else:
            show_notification = self.SETTINGS['notify_manual']
        self._notification( self.SNAME[int( profile )], show_notification )
        success, loglines = writeFile( profile, os.path.join(self.SETTINGS['ADDONDATAPATH'], 'profile'), 'w' )
        self.LW.log( loglines )
        s_cec = self.SETTINGS['profile%s_cec' % profile]
        if s_cec:
            self.LW.log( ['SENDING CEC COMMAND: %s' % self.CECCOMMANDS[s_cec]], xbmc.LOGINFO )
            xbmc.executebuiltin(self.CECCOMMANDS[s_cec])


    def _save( self ):
        ret, loglines = dialog.Dialog().start( self.XMLFILE, labels={10071: self.SETTINGS['ADDONLANGUAGE'](32100)}, buttons=self.ENABLEDPROFILES[1],
                                               thelist=10070, force_dialog=True )
        self.LW.log( loglines )
        self.LW.log( [ 'the returned value is %s' % str(ret) ] )
        if ret is None:
            return False
        else:
            button = self.ENABLEDPROFILES[0][ret]
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
            self.LW.log( ['JSON: %s' % str( jsonGet )] )
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
        jsonToWrite = json.dumps( self._convert( settingsToSave ) )
        self.LW.log( ['SAVING SETTING: %s' % self.SNAME[button]], xbmc.LOGINFO )
        success, loglines = writeFile( jsonToWrite, os.path.join( self.SETTINGS['ADDONDATAPATH'], 'profile%s.json' % str( button ) ), 'w' )
        self.LW.log( loglines )
        if success:
            self._notification( '%s %s (%s)' % (self.SETTINGS['ADDONLANGUAGE'](32102), str(button),
                                self.SNAME[button]), self.SETTINGS['notify_maintenance'] )


    def _toggle( self, mode ):
        loglines, profile = readFile( os.path.join( self.SETTINGS['ADDONDATAPATH'],'profile' ) )
        self.LW.log( loglines )
        if profile:
            if (len( self.APROFILE ) == 1) or (profile not in self.APROFILE):
                profile = self.APROFILE[0]
            else:
                ip = int( self.APROFILE.index(profile) )
                if len( self.APROFILE ) == ip:
                    try:
                        profile = self.APROFILE[0]
                    except IndexError:
                        profile = self.APROFILE[0]
                else:
                    try:
                        profile = self.APROFILE[ip + 1]
                    except IndexError:
                        profile = self.APROFILE[0]
        else:
            profile = self.APROFILE[0]
        self._profile( profile )
