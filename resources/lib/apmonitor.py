
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
        self._change_profile( self.SETTINGS['auto_default'], forceload=self.SETTINGS['force_auto_default'] )
        while not self.abortRequested():
            if self.waitForAbort( 10 ):
                break
        self.LW.log( ['background monitor version %s stopped' % self.SETTINGS['ADDONVERSION']], xbmc.LOGINFO )


    def onNotification( self, sender, method, data ):
        data = json.loads( data )
        if 'System.OnWake' in method:
            self.LW.log( ['MONITOR METHOD: %s DATA: %s' % (str( method ), str( data ))] )
            self._change_profile( self.SETTINGS['auto_default'] )
        if 'Player.OnStop' in method:
            self.LW.log( ['MONITOR METHOD: %s DATA: %s' % (str( method ), str( data ))] )
            self.waitForAbort( 1 )
            if not self.KODIPLAYER.isPlaying():
                self._change_profile( self.SETTINGS['auto_gui'] )
        if 'Player.OnPlay' in method:
            self.LW.log( ['MONITOR METHOD: %s DATA: %s' % (str( method ), str( data ))] )
            self._auto_switch( data )


    def onSettingsChanged( self ):
        self._init_vars()


    def _init_vars( self ):
        self.SETTINGS = loadSettings()
        self.PROFILESLIST = ['1', '2', '3', '4']
        # this only includes mappings we are 100% sure are accurate every time
        self.MAPTYPE = {'video': 'auto_videos', 'episode': 'auto_tvshows',
                        'musicvideo': 'auto_musicvideo', 'song': 'auto_music'}
        self.LW = Logger( preamble='[Audio Profiles Service]', logdebug=self.SETTINGS['debug'] )
        self.PROFILES = Profiles( self.SETTINGS, self.LW, auto=True )
        self.KODIPLAYER = xbmc.Player()
    

    def _auto_switch( self, data ):
        if self.SETTINGS['player_show']:
            self.LW.log( ['showing select menu'] )
            if self.PROFILES.changeProfile( 'popup' ) is not None:
                self.LW.log( ['option selected, returning'] )
                return
            self.LW.log( ['select menu timed out or was closed with no selection - continuing to auto select'] )
        try:
            thetype = data['item']['type']
        except IndexError:
            self.LW.log( ['data did not include valid item and/or type for playing media - aborting'] )
            return
        self.LW.log( ['the type is: %s' % thetype] )
        theset = self.MAPTYPE.get(thetype)
        if not theset:
            if thetype == 'movie':
                # if video is a PVR recording assign to auto_pvr_tv
                if self._check_playing_file( 'pvr://' ):
                    theset = 'auto_pvr_tv'
                # if video is not from library assign to auto_videos
                elif 'id' not in data['item']:
                    theset = 'auto_videos'
                # it must actually be a movie
                else:
                    theset = 'auto_movies'
            # distinguish pvr TV and pvr RADIO
            elif 'channel' in thetype and 'channeltype' in data['item']:
                if 'tv' in data['item']['channeltype']:
                    theset = 'auto_pvr_tv'
                elif 'radio' in data['item']['channeltype']:
                    theset = 'auto_pvr_radio'
                else:
                    theset = 'auto_unknown'
            # detect cdda that kodi return as unknown
            elif thetype == 'unknown':
                if self._check_playing_file( 'cdda://' ):
                    theset = 'auto_music'
                else:
                    theset = 'auto_unknown'
            else:
                theset = 'auto_unknown'
        self.LW.log( ['Setting parsed: %s' % theset] )
        self._change_profile( self.SETTINGS[theset] )


    def _change_profile( self, profile, forceload=False ):
        if profile in self.PROFILESLIST:
            last_profile = self._get_last_profile()
            self.LW.log( ['Last loaded profile: %s To switch profile: %s' % (last_profile, profile)] )
            if last_profile != profile or forceload:
                self.PROFILES.changeProfile( profile )
            else:
                self.LW.log( ['Same profile - profiles not switched'] )
        elif profile == str( len( self.PROFILESLIST ) + 1 ):
            self.LW.log( ['this auto switch setting is set to show the select menu - showing menu'] )
            self.PROFILES.changeProfile( 'popup' )


    def _check_playing_file( self, thestr ):
        try:
            thefile = self.KODIPLAYER.getPlayingFile()
        except RuntimeError:
            self.LW.log( ['error trying to get playing file from Kodi'] )
            return False
        self.LW.log( ['the playing file is: %s' % thefile] )
        return thefile.startswith( thestr )


    def _get_last_profile( self ):
        loglines, profile = readFile( os.path.join( self.SETTINGS['ADDONDATAPATH'], 'profile' ) )
        self.LW.log( loglines )
        if profile in self.PROFILESLIST:
            return profile
        else:
            return ''
