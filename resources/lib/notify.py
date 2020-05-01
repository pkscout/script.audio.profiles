# -*- coding: utf-8 -*-
# *  Credits:
# *
# *  original Audio Profiles code by Regss
# *  updates and additions through v1.4.1 by notoco and CtrlGy
# *  updates and additions since v1.4.2 by pkscout

from kodi_six import xbmc, xbmcgui
from resources.lib.addoninfo import *


def popup(msg, force=False, title=''):
    if 'true' in ADDON.getSetting('notify') or force is True:
        if title:
            title = '%s - %s' % (ADDON_NAME, title)
        else:
            title = ADDON_NAME
        notify_time = ADDON.getSetting('notify_time')
        if notify_time:
            notify_time = int(notify_time) * 1000
        else:
            notify_time = 5000
        xbmcgui.Dialog().notification(title, msg, icon=ADDON_ICON, time=notify_time)


def logInfo(msg):
    xbmc.log('[%s] %s' % (ADDON_NAME, msg), level=xbmc.LOGINFO)


def logError(msg):
    xbmc.log('[%s] %s' % (ADDON_NAME, msg), level=xbmc.LOGERROR)


def logDebug(msg):
    if ADDON.getSetting('debug').lower() == 'true':
        xbmc.log('[%s] %s' % (ADDON_NAME, msg), level=xbmc.LOGDEBUG)


