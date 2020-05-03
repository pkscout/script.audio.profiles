
import sys
from kodi_six import xbmc
from resources.lib.xlogger import Logger
from resources.lib.apsettings import loadSettings
from resources.lib.profiles import Profiles



class Main:

    def __init__( self ):
        settings = loadSettings()
        lw = Logger( preamble='[Audio Profiles]', logdebug=settings['debug'] )
        lw.log( ['script version %s started' % settings['ADDONVERSION']], xbmc.LOGINFO )
        lw.log( ['debug logging set to %s' % settings['debug']], xbmc.LOGINFO )
        lw.log( ['SYS.ARGV: %s' % str(sys.argv)] )
        lw.log( ['loaded settings', settings] )
        profiles = Profiles( settings, lw )
        try:
            mode = sys.argv[1]
        except IndexError:
            mode = False
        lw.log( ['MODE: %s' % str(mode)] )
        profiles.changeProfile( mode )
        lw.log( ['script version %s stopped' % settings['ADDONVERSION']], xbmc.LOGINFO )
