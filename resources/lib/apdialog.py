import os
from kodi_six import xbmc, xbmcgui
from resources.lib.fileops import checkPath

KODIMONITOR  = xbmc.Monitor()
KODIPLAYER   = xbmc.Player()



class Dialog:

    def start( self, settings, labels=None, textboxes=None, buttons=None, thelist=0, force_dialog=False ):
        loglines = []
        count = 0
        delay = settings['player_autoclose_delay']
        autoclose = settings['player_autoclose']
        loglines.append( 'set background menu diffusion to %s' % settings['menu_diffusion'] )
        loglines.append( 'using menu.xml from %s' % settings['SKINNAME'] )
        display = Show( 'menu.xml', settings['ADDONPATH'], settings['SKINNAME'],
                        diffusion=settings['menu_diffusion'], labels=labels, textboxes=textboxes,
                        buttons=buttons, thelist=thelist )
        display.show()
        while (KODIPLAYER.isPlaying() or force_dialog) and not display.CLOSED and not KODIMONITOR.abortRequested():
            loglines.append( 'the current returned value from display is: %s' % str(display.DIALOGRETURN) )
            loglines.append( 'the current returned close status from display is: %s' % str(display.CLOSED) )
            if autoclose and not force_dialog:
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

    def __init__( self, xml_file, script_path, defaultSkin, diffusion='90', labels=None, textboxes=None, buttons=None, thelist=None ):
        self.DIFFUSION = diffusion
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
        xbmcgui.Window( 10000 ).setProperty( 'ap_diffusion', self.DIFFUSION )
        xbmcgui.Window( 10000 ).setProperty( 'ap_buttons', str( len( self.BUTTONS ) ) )


    def onAction( self, action ):
        if action in [self.ACTION_PREVIOUS_MENU, self.ACTION_NAV_BACK]:
            self.CLOSED = True
            self.close()

    def onClick( self, controlID ):
        self.DIALOGRETURN = self.getControl( controlID ).getSelectedPosition()
        self.close()
