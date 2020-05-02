# v.0.2.0

from kodi_six import xbmc
import json, os
from resources.lib.fileops import *
from resources.lib.xlogger import Logger
from resources.lib.apsettings import loadSettings
from resources.lib.profiles import Profiles



class apMonitor( xbmc.Monitor ):

    def __init__( self ):
        xbmc.Monitor.__init__( self )
        self._init_vars()
        self.LW.log( ['background monitor version %s started' % self.SETTINGS['ADDONVERSION']], xbmc.LOGINFO )
        self.LW.log( ['debug logging set to %s' % self.SETTINGS['debug']], xbmc.LOGINFO )
        self._chage_profile( self.SETTINGS['auto_default'], forceload=self.SETTINGS['force_auto_default'] )
        while not self.abortRequested():
            if self.waitForAbort( 10 ):
                break
        self.LW.log( ['background monitor version %s stopped' % self.SETTINGS['ADDONVERSION']], xbmc.LOGINFO )


    def onNotification( self, sender, method, data ):
        data = json.loads( data )
        if 'System.OnWake' in method:
            self.LW.log( ['MONITOR METHOD: %s DATA: %s' % (str( method ), str( data ))] )
            self._chage_profile( self.SETTINGS['auto_default'] )
        if 'Player.OnStop' in method:
            self.LW.log( ['MONITOR METHOD: %s DATA: %s' % (str( method ), str( data ))] )
            self.waitForAbort( 1 )
            if not self.KODIPLAYER.isPlaying():
                self.SUSPENDAUTOCHANGE = False
                self._chage_profile( self.SETTINGS['auto_gui'] )
                self.SUSPENDAUTOCHANGE = True
        if 'Player.OnPlay' in method:
            self.LW.log( ['MONITOR METHOD: %s DATA: %s' % (str( method ), str( data ))] )
            if 'item' in data and 'type' in data['item']:
                self._auto_switch( data )


    def onSettingsChanged( self ):
        self._init_vars()


    def _init_vars( self ):
        self.SETTINGS = loadSettings()
        self.PROFILESLIST = ['1', '2', '3', '4']
        self.MAPTYPE = {'movie': 'auto_movies', 'video': 'auto_videos', 'episode': 'auto_tvshows', 'channel': 'auto_pvr',
                        'musicvideo': 'auto_musicvideo', 'song': 'auto_music', 'unknown': 'auto_unknown'}
        self.SUSPENDAUTOCHANGE = False
        self.SETFORSUSPEND = None
        self.LW = Logger( preamble='[Audio Profiles Service]', logdebug=self.SETTINGS['debug'] )
        self.PROFILES = Profiles( self.SETTINGS, self.LW, auto=True )
        self.KODIPLAYER = xbmc.Player()
    

    def _auto_switch( self, data ):
        thetype = data['item']['type']
        theset =self.MAPTYPE.get(thetype)
        self.LW.log( ['the data are:'] )
        self.LW.log( [data] )
        if self.SETTINGS['player_show']:
            if self.PROFILES.changeProfile( 'popup' ) is not None:
                return
        # if video is not from library assign to auto_videos
        if 'movie' in thetype and 'id' not in data['item']:
            theset = 'auto_videos'
        # distinguish pvr TV and pvr RADIO
        if 'channel' in thetype and 'channeltype' in data['item']:
            if 'tv' in data['item']['channeltype']:
                theset = 'auto_pvr_tv'
            elif 'radio' in data['item']['channeltype']:
                theset = 'auto_pvr_radio'
            else:
                theset = None
        # detect cdda that kodi return as unknown
        if 'unknown' in thetype and 'player' in data and 'playerid' in data['player']:
            json_str = xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "id": "1", "method": "Player.GetItem", "params": {"playerid": %s, "properties": ["file"]}}' % str(data['player']['playerid'])
            )
            json_ret = json.loads(json_str)
            try:
                thefile = json_ret['result']['item']['file']
            except (IndexError, KeyError, ValueError):
                thefile = ''
            if thefile.startswith( 'cdda://' ):
                theset = 'auto_music'
        self.LW.log( ['Setting parsed: %s' % str( theset )] )
        # cancel suspend auto change when media thetype change
        if theset != self.SETFORSUSPEND:
            self.SUSPENDAUTOCHANGE = False
            self.SETFORSUSPEND = theset
        if theset is not None:
            self._chage_profile( self.SETTINGS[theset] )
            self.SUSPENDAUTOCHANGE = True


    def _chage_profile( self, profile, forceload=False ):
        if profile in self.PROFILESLIST:
            # get last loaded profile
            lastProfile = self._get_last_profile()
            self.LW.log( ['Last loaded profile: %s To switch profile: %s' % (lastProfile, profile)] )
            if (lastProfile != profile and not self.SUSPENDAUTOCHANGE) or forceload:
                self.PROFILES.changeProfile( profile )
            else:
                self.LW.log( ['Switching omitted (same profile) or switching is susspend'] )


    def _get_last_profile( self ):
        loglines, p = readFile( os.path.join( self.SETTINGS['ADDONDATAPATH'], 'profile' ) )
        self.LW.log( loglines )
        if p in self.PROFILESLIST:
            return p
        else:
            return ''
