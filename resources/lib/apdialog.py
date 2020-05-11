
import os
from kodi_six import xbmc, xbmcgui
from resources.lib.fileops import checkPath, listDirectory

KODIMONITOR  = xbmc.Monitor()
KODIPLAYER   = xbmc.Player()
SKINVALUESLIST   = { 'default': {'res':'720p', 'diagw':400, 'toph':50, 'bottomh':10, 'buttonh':45},
                     'skin.ace2': {'res':'1080i', 'diagw':600, 'toph':95, 'bottomh':0, 'buttonh':45},
                     'skin.aeonmq8': {'res':'720p', 'diagw':400, 'toph':58, 'bottomh':0, 'buttonh':50},
                     'skin.aeon.nox.silvo': {'res':'1080i', 'diagw':600, 'toph':80, 'bottomh':50, 'buttonh':60},
                     'skin.aeon.tajo': {'res':'1080i', 'diagw':720, 'toph':75, 'bottomh':15, 'buttonh':60},
                     'skin.amber': {'res':'1080i', 'diagw':600, 'toph':105, 'bottomh':53, 'buttonh':60},
                     'skin.apptv': {'res':'720p', 'diagw':500, 'toph':50, 'bottomh':15, 'buttonh':48},
                     'skin.aura': {'res':'720p', 'diagw':300, 'toph':54, 'bottomh':10, 'buttonh':47},
                     'skin.bello.7': {'res':'720p', 'diagw':405, 'toph':112, 'bottomh':22, 'buttonh':37},
                     'skin.confluence': {'res':'720p', 'diagw':400, 'toph':60, 'bottomh':25, 'buttonh':40},
                     'skin.estuary': {'res':'1080i', 'diagw':600, 'toph':75, 'bottomh':0, 'buttonh':70},
                     'skin.embuary-leia': {'res':'1080i', 'diagw':500, 'toph':111, 'bottomh':61, 'buttonh':50},
                     'skin.quartz': {'res':'720p', 'diagw':480, 'toph':61, 'bottomh':10, 'buttonh':50},
                     'skin.rapier': {'res':'720p', 'diagw':400, 'toph':69, 'bottomh':32, 'buttonh':37}
                   }



class Dialog:

    def start( self, settings, title='', buttons=None, force_dialog=False ):
        self.SETTINGS = settings
        self.TITLE = title
        self.BUTTONS = buttons
        self.FORCEDIALOG = force_dialog
        self.LOGLINES = []
        if self.SETTINGS['use_custom_skin_menu']:
            return self._custom()
        else:
            return self._built_in()


    def _built_in( self ):
        self.LOGLINES = []
        delay = self.SETTINGS['player_autoclose_delay'] * 1000
        autoclose = self.SETTINGS['player_autoclose']
        self.LOGLINES.append( 'using built-in dialog box' )
        if not autoclose or self.FORCEDIALOG:
            d_return = xbmcgui.Dialog().select( self.TITLE, self.BUTTONS )
        else:
            d_return = xbmcgui.Dialog().select( self.TITLE, self.BUTTONS, autoclose=delay )
        self.LOGLINES.append( 'the final returned value from the dialog box is: %s' % str( d_return ) )
        if d_return == -1:
            d_return = None
        return d_return, self.LOGLINES


    def _custom( self ):
        self.LOGLINES = []
        count = 0
        delay = self.SETTINGS['player_autoclose_delay']
        autoclose = self.SETTINGS['player_autoclose']
        current_skin = xbmc.getSkinDir()
        skin, skin_values = self._get_skin_info( current_skin )
        self.LOGLINES.append( 'for skin %s using %s' % (current_skin, skin) )
        self.LOGLINES.append( 'using skin values of:' )
        self.LOGLINES.append( skin_values )
        display = Show( 'ap-menu.xml', self.SETTINGS['ADDONPATH'], skin, skin_values['res'],
                        skin_values=skin_values, title=self.TITLE, buttons=self.BUTTONS )
        display.show()
        while (KODIPLAYER.isPlaying() or self.FORCEDIALOG) and not display.CLOSED and not KODIMONITOR.abortRequested():
            self.LOGLINES.append( 'the current returned value from display is: %s' % str( display.DIALOGRETURN ) )
            self.LOGLINES.append( 'the current returned close status from display is: %s' % str( display.CLOSED ) )
            if autoclose and not self.FORCEDIALOG:
                if count >= delay or display.DIALOGRETURN is not None:
                    break
                count = count + 1
            else:
                if display.DIALOGRETURN is not None:
                    break
            KODIMONITOR.waitForAbort( 1 )
        self.LOGLINES = self.LOGLINES + display.LOGLINES
        self.LOGLINES.append( 'the final returned value from display is: %s' % str(display.DIALOGRETURN) )
        self.LOGLINES.append( 'the final returned close status from display is: %s' % str(display.CLOSED) )
        d_return = display.DIALOGRETURN
        del display
        return d_return, self.LOGLINES


    def _get_skin_info( self, current_skin ):
        default_skin = 'Default'
        skin_list, loglines = listDirectory( os.path.join( self.SETTINGS['ADDONPATH'], 'resources', 'skins' ), thefilter='folders' )
        self.LOGLINES = self.LOGLINES + loglines
        if current_skin in skin_list:
            self.LOGLINES.append( 'found %s in list of skins, returning it as the skin' % current_skin )
            return current_skin, SKINVALUESLIST.get( current_skin.lower() )
        keep_trying = True
        skin_parts = current_skin.split('.')
        skin_glue = len( skin_parts )
        while keep_trying:
            skin_test = '.'.join( skin_parts[:skin_glue] )
            success, self.LOGLINES = checkPath( os.path.join( self.SETTINGS['ADDONPATH'], 'resources', 'skins', skin_test, '' ), createdir=False )
            if success:
                default_skin = skin_test
                keep_trying = False
            skin_glue -= 1
            if skin_glue == 0:
                keep_trying = False
        self.LOGLINES.append( 'returning %s as the skin for skin %s' % (default_skin, current_skin) )
        return default_skin, SKINVALUESLIST.get( default_skin.lower() )
    


class Show( xbmcgui.WindowXMLDialog ):

    def __init__( self, xml_file, script_path, defaultSkin, defaultRes, skin_values=None, title='', buttons=None ):
        """Shows a Kodi WindowXMLDialog."""
        self.DIALOGRETURN = None
        self.CLOSED = False
        self.ACTION_PREVIOUS_MENU = 10
        self.ACTION_NAV_BACK = 92
        self.SKINVALUES = skin_values
        self.TITLE = title
        if buttons:
            self.BUTTONS = buttons
        else:
            self.BUTTONS = []
        self.LOGLINES = []


    def onInit( self ):
        x, y, bottom_y = self._get_coordinates()
        if x and y:
            self.getControl( 10072 ).setPosition( x, y )
        if bottom_y:
            self.getControl( 10073 ).setPosition( 0, bottom_y)
        self.getControl( 10071 ).setLabel( self.TITLE )
        the_list = self.getControl( 10070 )
        for button_text in self.BUTTONS:
            self.LOGLINES.append( 'setting list item to: %s' % button_text )
            the_list.addItem( xbmcgui.ListItem( button_text ) )
        self.setFocus( the_list )


    def onAction( self, action ):
        if action in [self.ACTION_PREVIOUS_MENU, self.ACTION_NAV_BACK]:
            self.CLOSED = True
            self.close()


    def onClick( self, controlID ):
        self.DIALOGRETURN = self.getControl( controlID ).getSelectedPosition()
        self.close()


    def _get_coordinates( self ):
        if not self.SKINVALUES:
            return 0, 0, 0
        dialog_height = (len( self.BUTTONS ) * self.SKINVALUES['buttonh']) + self.SKINVALUES['toph'] + self.SKINVALUES['bottomh']
        if self.SKINVALUES['res'] == '720p':
            screen_width = 1280
            screen_height = 720
        else:
            screen_width = 1920
            screen_height = 1080
        x = (screen_width - self.SKINVALUES['diagw']) // 2
        y = (screen_height - dialog_height) // 2
        if self.SKINVALUES['bottomh']:
            bottom_y = dialog_height - self.SKINVALUES['bottomh']
        else:
            bottom_y = 0
        return x, y, bottom_y
