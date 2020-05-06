from kodi_six import xbmc, xbmcgui

KODIMONITOR  = xbmc.Monitor()
KODIPLAYER   = xbmc.Player()



class Dialog:

    def start( self, settings, labels=None, textboxes=None, buttons=None, thelist=0, force_dialog=False ):
        self.SETTINGS = settings
        self.LABELS = labels
        self.TEXTBOXES = textboxes
        self.BUTTONS = buttons
        self.THELIST = thelist
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
            d_return = xbmcgui.Dialog().select( self.LABELS[10071], self.BUTTONS )
        else:
            d_return = xbmcgui.Dialog().select( self.LABELS[10071], self.BUTTONS, autoclose=delay )
        loglines.append( 'the final returned value from the dialog box is: %s' % str( d_return ) )
        if d_return == -1:
            d_return = None
        return d_return, loglines


    def _custom( self ):
        loglines = []
        count = 0
        delay = self.SETTINGS['player_autoclose_delay']
        autoclose = self.SETTINGS['player_autoclose']
        xmlfilename = 'ap-menu-%s.xml' % str( len( self.BUTTONS ) )
        loglines.append( 'using %s from %s' % (xmlfilename, self.SETTINGS['SKINNAME']) )
        display = Show( xmlfilename, self.SETTINGS['ADDONPATH'], self.SETTINGS['SKINNAME'], labels=self.LABELS,
                        textboxes=self.TEXTBOXES, buttons=self.BUTTONS, thelist=self.THELIST )
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
        loglines.append( 'the final returned value from display is: %s' % str(display.DIALOGRETURN) )
        loglines.append( 'the final returned close status from display is: %s' % str(display.CLOSED) )
        d_return = display.DIALOGRETURN
        del display
        return d_return, loglines



class Show( xbmcgui.WindowXMLDialog ):

    def __init__( self, xml_file, script_path, defaultSkin, labels=None, textboxes=None, buttons=None, thelist=None ):
        """Shows a Kodi WindowXMLDialog."""
        self.DIALOGRETURN = None
        self.CLOSED = False
        self.ACTION_PREVIOUS_MENU = 10
        self.ACTION_NAV_BACK = 92
        if labels:
            self.LABELS = labels
        else:
            self.LABELS = {}
        if textboxes:
            self.TEXTBOXES = textboxes
        else:
            self.TEXTBOXES = {}
        if buttons:
            self.BUTTONS = buttons
        else:
            self.BUTTONS = []
        self.THELIST = thelist


    def onInit( self ):
        for label, label_text in list( self.LABELS.items() ):
            self.getControl( label ).setLabel( label_text )
        for textbox, textbox_text in list( self.TEXTBOXES.items() ):
            self.getControl( textbox ).setText( textbox_text )
        self.listitem = self.getControl( self.THELIST )
        for button_text in self.BUTTONS:
            self.listitem.addItem( xbmcgui.ListItem( button_text ) )
        self.setFocus( self.listitem )


    def onAction( self, action ):
        if action in [self.ACTION_PREVIOUS_MENU, self.ACTION_NAV_BACK]:
            self.CLOSED = True
            self.close()

    def onClick( self, controlID ):
        self.DIALOGRETURN = self.getControl( controlID ).getSelectedPosition()
        self.close()
