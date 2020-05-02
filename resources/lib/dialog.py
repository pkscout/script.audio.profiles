# v.2.0

from kodi_six import xbmc, xbmcgui
from resources.lib.kodisettings import *

KODIMONITOR  = xbmc.Monitor()
KODIPLAYER   = xbmc.Player()



class Dialog:

    def start( self, xml_file, labels=None, textboxes=None, buttons=None, thelist=0, force_dialog=False ):
        self.LOGLINES = []
        count = 0
        if getSettingBool( 'player_show' ):
            delay = getSettingInt( 'player_autoclose_delay', default=10 )
            autoclose = getSettingBool( 'player_autoclose' )
        else:
            delay = 10
            autoclose = False
        display = Show(xml_file, ADDONPATH, labels=labels, textboxes=textboxes, buttons=buttons, thelist=thelist)
        display.show()
        while (KODIPLAYER.isPlaying() or force_dialog) and not KODIMONITOR.abortRequested():
            self.LOGLINES.append( 'the current returned value from display is: %s' % str(display.ret) )
            if autoclose and not force_dialog:
                if count >= delay or display.ret is not None:
                    break
                count = count + 1
            else:
                if display.ret is not None:
                    break
            KODIMONITOR.waitForAbort( 1 )
        ret = display.ret
        del display
        return ret, self.LOGLINES



class Show( xbmcgui.WindowXMLDialog ):

    def __init__( self, xmlFile, resourcePath, labels, textboxes, buttons, thelist ):
        self.ret = None
        if labels:
            self.labels = labels
        else:
            self.labels = {}
        if textboxes:
            self.textboxes = textboxes
        else:
            self.textboxes = {}
        if buttons:
            self.buttons = buttons
        else:
            self.buttons = []
        self.thelist = thelist


    def onInit( self ):
        # set labels
        for label, label_text in list( self.labels.items() ):
            self.getControl( label ).setLabel( label_text )
        # set textboxes
        for textbox, textbox_text in list( self.textboxes.items() ):
            self.getControl( textbox ).setText( textbox_text )
        # set buttons
        self.listitem = self.getControl( self.thelist )
        for button_text in self.buttons:
            self.listitem.addItem( xbmcgui.ListItem( button_text ) )
        # focus on list
        self.setFocus( self.listitem )
        # set amount of buttons for background height
        xbmcgui.Window( 10000 ).setProperty( ADDONNAME + '_items', str( len( self.buttons ) ) )


    def onClick( self, controlID ):
        # return selected button
        self.ret = self.getControl( controlID ).getSelectedPosition()
        self.close()
