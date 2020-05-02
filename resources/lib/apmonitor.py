# -*- coding: utf-8 -*-
# *  Credits:
# *
# *  original Audio Profiles code by Regss
# *  updates and additions through v1.4.1 by notoco and CtrlGy
# *  updates and additions since v1.4.2 by pkscout

from kodi_six import xbmc
import json, os
from resources.lib.fileops import *
from resources.lib.xlogger import Logger
from resources.lib.kodisettings import *

PROFILES          = ['1', '2', '3', '4']
MAPTYPE           = {'movie': 'auto_movies', 'video': 'auto_videos', 'episode': 'auto_tvshows', 'channel': 'auto_pvr',
                     'musicvideo': 'auto_musicvideo', 'song': 'auto_music', 'unknown': 'auto_unknown'}
SUSPENDAUTOCHANGE = False
SETFORSUSPEND     = None
LOGDEBUG          = getSettingBool( 'debug' )
LW                = Logger( preamble='[Audio Profiles Service]', logdebug=LOGDEBUG )
KODIPLAYER        = xbmc.Player()



class Monitor( xbmc.Monitor ):

    def __init__( self ):
        LW.log( ['background monitor version %s started' % ADDONVERSION], xbmc.LOGINFO )
        LW.log( ['debug logging set to %s' % LOGDEBUG], xbmc.LOGINFO )
        xbmc.Monitor.__init__( self )
        # default for kodi start
        self.changeProfile( getSettingString( 'auto_default' ), forceload=getSettingBool( 'force_auto_default' ) )
        while not self.abortRequested():
            if self.waitForAbort( 10 ):
                break
        LW.log( ['background monitor version %s stopped' % ADDONVERSION], xbmc.LOGINFO )


    def onNotification( self, sender, method, data ):
        global SUSPENDAUTOCHANGE
        global SETFORSUSPEND
        data = json.loads( data )
        if 'System.OnWake' in method:
            LW.log( ['MONITOR METHOD: %s DATA: %s' % (str( method ), str( data ))] )
            # default for kodi wakeup
            self.changeProfile( getSettingString('auto_default') )
        if 'Player.OnStop' in method:
            LW.log( ['MONITOR METHOD: %s DATA: %s' % (str( method ), str( data ))] )
            self.waitForAbort( 1 )
            if not KODIPLAYER.isPlaying():
                SUSPENDAUTOCHANGE = False
                self.changeProfile(getSettingString('auto_gui'))
        if 'Player.OnPlay' in method:
            LW.log( ['MONITOR METHOD: %s DATA: %s' % (str( method ), str( data ))] )
            # auto switch
            if 'item' in data and 'type' in data['item']:
                self.autoSwitch( data )


    def autoSwitch( self, data ):
        global SUSPENDAUTOCHANGE
        global SETFORSUSPEND
        thetype = data['item']['type']
        theset = MAPTYPE.get(thetype)
        LW.log( ['the data are:'] )
        LW.log( [data] )
        if getSettingBool( 'player_show' ):
            xbmc.executebuiltin( 'RunScript(%s, popup)' % ADDONNAME )
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
            jsonS = xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "id": "1", "method": "Player.GetItem", "params": {"playerid": %s, "properties": ["file"]}}' % str(data['player']['playerid'])
                                       )
            jsonR = json.loads(jsonS)
            try:
                thefile = jsonR['result']['item']['file']
            except (IndexError, KeyError, ValueError):
                thefile = ''
            if thefile.startswith( 'cdda://' ):
                theset = 'auto_music'
        LW.log( ['Setting parsed: %s' % str(theset)] )
        # cancel susspend auto change when media thetype change
        if theset != SETFORSUSPEND:
            SUSPENDAUTOCHANGE = False
            SETFORSUSPEND = theset
        if theset is not None:
            self.changeProfile( getSettingString( theset ) )
            SUSPENDAUTOCHANGE = True


    def changeProfile( self, profile, forceload=False ):
        if profile in PROFILES:
            # get last loaded profile
            lastProfile = self.getLastProfile()
            LW.log( ['Last loaded profile: %s To switch profile: %s' % (lastProfile, profile)] )
            if (lastProfile != profile and not SUSPENDAUTOCHANGE) or forceload:
                xbmc.executebuiltin( 'RunScript(%s, %s) ' % (ADDONNAME, profile) )
            else:
                LW.log( ['Switching omitted (same profile) or switching is susspend'] )


    def getLastProfile( self ):
        loglines, p = readFile( os.path.join( ADDONDATAPATH, 'profile' ) )
        LW.log( loglines )
        if p in PROFILES:
            return p
        else:
            return ''
