
from kodi_six import xbmc, xbmcgui

KODIMONITOR  = xbmc.Monitor()
KODIPLAYER   = xbmc.Player()



class Dialog:

    def start( self, settings, title='', buttons=None, force_dialog=False ):
        self.SETTINGS = settings
        self.TITLE = title
        self.BUTTONS = buttons
        self.FORCEDIALOG = force_dialog
        if self.SETTINGS['use_custom_skin_menu']:
            return self._custom()
        else:
            return self._built_in()


    def _built_in( self ):
        loglines = []
        delay = self.SETTINGS['player_autoclose_delay'] * 1000
        autoclose = self.SETTINGS['player_autoclose']
        loglines.append( 'using built-in dialog box' )
        if not autoclose or self.FORCEDIALOG:
            d_return = xbmcgui.Dialog().select( self.TITLE, self.BUTTONS )
        else:
            d_return = xbmcgui.Dialog().select( self.TITLE, self.BUTTONS, autoclose=delay )
        loglines.append( 'the final returned value from the dialog box is: %s' % str( d_return ) )
        if d_return == -1:
            d_return = None
        return d_return, loglines


    def _custom( self ):
        loglines = []
        count = 0
        delay = self.SETTINGS['player_autoclose_delay']
        autoclose = self.SETTINGS['player_autoclose']
        xmlfilename = 'ap-menu.xml'
        loglines.append( 'using %s from %s' % (xmlfilename, self.SETTINGS['SKINNAME']) )
        display = Show( xmlfilename, self.SETTINGS['ADDONPATH'], self.SETTINGS['SKINNAME'], '720p',
                        title=self.TITLE, buttons=self.BUTTONS )
        display.show()
        while (KODIPLAYER.isPlaying() or self.FORCEDIALOG) and not display.CLOSED and not KODIMONITOR.abortRequested():
            loglines.append( 'the current returned value from display is: %s' % str( display.DIALOGRETURN ) )
            loglines.append( 'the current returned close status from display is: %s' % str( display.CLOSED ) )
            if autoclose and not self.FORCEDIALOG:
                if count >= delay or display.DIALOGRETURN is not None:
                    break
                count = count + 1
            else:
                if display.DIALOGRETURN is not None:
                    break
            KODIMONITOR.waitForAbort( 1 )
        loglines = loglines + display.LOGLINES
        loglines.append( 'the final returned value from display is: %s' % str(display.DIALOGRETURN) )
        loglines.append( 'the final returned close status from display is: %s' % str(display.CLOSED) )
        d_return = display.DIALOGRETURN
        del display
        return d_return, loglines



class Show( xbmcgui.WindowXMLDialog ):

    def __init__( self, xml_file, script_path, defaultSkin, defaultRes, title='', buttons=None ):
        """Shows a Kodi WindowXMLDialog."""
        self.DIALOGRETURN = None
        self.CLOSED = False
        self.ACTION_PREVIOUS_MENU = 10
        self.ACTION_NAV_BACK = 92
        self.SKINNAME = defaultSkin
        self.TITLE = title
        if buttons:
            self.BUTTONS = buttons
        else:
            self.BUTTONS = []
        self.LOGLINES = []


    def onInit( self ):
        x, y, bottom_y = self._get_coordinates()
        self.getControl( 10072 ).setPosition( x, y )
        if bottom_y:
            self.getControl( 10073 ).setPosition( 0, bottom_y)
        self.getControl( 10071 ).setLabel( self.TITLE )
        the_list = self.getControl( 10070 )
        for button_text in self.BUTTONS:
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
        skin_values = self._get_skin_values()
        self.LOGLINES.append( 'got back skin values of:' )
        self.LOGLINES.append( skin_values )
        dialog_height = (len( self.BUTTONS ) * skin_values['buttonh']) + skin_values['toph'] + skin_values['bottomh']
        x = (1280 - skin_values['diagw']) // 2
        y = (720 - dialog_height) // 2
        if skin_values['bottomh']:
            bottom_y = dialog_height - skin_values['bottomh']
        else:
            bottom_y = 0
        return x + skin_values['xoffset'], y + skin_values['yoffset'], bottom_y


    def _get_skin_values( self ):
        skin_values = { 'ap-default': {'diagw':400, 'toph':50, 'bottomh':10, 'buttonh':45, 'xoffset':0, 'yoffset':0},
                        'ap-skin.ace2': {'diagw':400, 'toph':58, 'bottomh':0, 'buttonh':45, 'xoffset':0, 'yoffset':0},
                        'ap-skin.aeonmq8': {'diagw':400, 'toph':58, 'bottomh':0, 'buttonh':50, 'xoffset':0, 'yoffset':0},
                        'ap-skin.aeon.nox.silvo': {'diagw':400, 'toph':74, 'bottomh':34, 'buttonh':40, 'xoffset':0, 'yoffset':0},
                        'ap-skin.aeon.tajo': {'diagw':480, 'toph':50, 'bottomh':10, 'buttonh':40, 'xoffset':0, 'yoffset':0},
                        'ap-skin.amber': {'diagw':400, 'toph':70, 'bottomh':35, 'buttonh':40, 'xoffset':0, 'yoffset':0},
                        'ap-skin.confluence': {'diagw':400, 'toph':60, 'bottomh':25, 'buttonh':40, 'xoffset':0, 'yoffset':0},
                        'ap-skin.estuary': {'diagw':400, 'toph':50, 'bottomh':0, 'buttonh':45, 'xoffset':0, 'yoffset':0},
                        'ap-skin.quartz': {'diagw':480, 'toph':61, 'bottomh':10, 'buttonh':50, 'xoffset':0, 'yoffset':0},
                        'ap-skin.rapier': {'diagw':400, 'toph':69, 'bottomh':32, 'buttonh':37, 'xoffset':0, 'yoffset':0}
                      }
        return skin_values[self.SKINNAME.lower()]
