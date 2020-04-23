# -*- coding: utf-8 -*-

from kodi_six import xbmc, xbmcaddon, xbmcgui

ADDON = xbmcaddon.Addon()
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')


def popup(msg, force=False, title=''):
    if 'true' in ADDON.getSetting('notify') or force is True:
        if title:
            title = '%s - %s' % (ADDON_NAME, title)
        else:
            title = ADDON_NAME
        xbmcgui.Dialog().notification(title, msg, icon=ADDON_ICON)


def logNotice(msg):
    xbmc.log('[%s] %s' % (ADDON_NAME, msg), level=xbmc.LOGNOTICE)


def logError(msg):
    xbmc.log('[%s] %s' % (ADDON_NAME, msg), level=xbmc.LOGERROR)


def logDebug(msg):
    xbmc.log('[%s] %s' % (ADDON_NAME, msg), level=xbmc.LOGDEBUG)


