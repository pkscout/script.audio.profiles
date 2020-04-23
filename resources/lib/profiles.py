# -*- coding: utf-8 -*-

from kodi_six import xbmc, xbmcaddon, xbmcgui, xbmcvfs
import json, os, sys
import resources.lib.dialog as dialog
import resources.lib.notify as notify

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_PATH = xbmc.translatePath(ADDON.getAddonInfo('path'))
ADDON_PATH_DATA = xbmc.translatePath( ADDON.getAddonInfo('profile') )
ADDON_LANG = ADDON.getLocalizedString

# set vars
sName = {
    1: ADDON.getSetting('name1'),
    2: ADDON.getSetting('name2'),
    3: ADDON.getSetting('name3'),
    4: ADDON.getSetting('name4')
}
sProfile = {
    1: ADDON.getSetting('profile1'),
    2: ADDON.getSetting('profile2'),
    3: ADDON.getSetting('profile3'),
    4: ADDON.getSetting('profile4')
}
cecCommands = ['', 'CECActivateSource', 'CECStandby', 'CECToggleState']
xbmc_version = int(xbmc.getInfoLabel('System.BuildVersion')[0:2])

def convert(data):
    if isinstance(data, bytes):      return data.decode()
    if isinstance(data, (str, int)): return str(data)
    if isinstance(data, dict):       return dict(map(convert, data.items()))
    if isinstance(data, tuple):      return tuple(map(convert, data))
    if isinstance(data, list):       return list(map(convert, data))
    if isinstance(data, set):        return set(map(convert, data))



class PROFILES:

    def __init__(self):
        notify.logDebug('[SYS.ARGV]: ' + str(sys.argv))
        notify.logDebug('[XBMC VERSION]: ' + str(xbmc_version))
        self.xmlFile = 'script-audio-profiles-menu.xml'
        # detect mode, check args
        if (len(sys.argv) < 2 or len(sys.argv[0]) == 0):
            mode = False
        else:
            mode = str(sys.argv[1])
        notify.logDebug('[MODE]: ' + str(mode))
        self.start(mode)


    def start(self, mode):
        xbmcgui.Window(10000).clearProperty(ADDON_ID + '_autoclose')
        # check is profiles is set
        if 'true' not in sProfile.values():
            notify.popup(ADDON_LANG(32105))
            xbmcaddon.Addon(id=ADDON_ID).openSettings()
        if mode is False:
            self.save()
            return
        if mode == 'popup':
            enabledProfiles = self.getEnabledProfiles()
            xbmcgui.Window(10000).setProperty(ADDON_ID + '_autoclose',
                                              '1' if 'true' in ADDON.getSetting('player_autoclose') else '0')
            ret = dialog.DIALOG().start(self.xmlFile, labels={10071: ADDON_LANG(32106)}, buttons=enabledProfiles[1],
                                        thelist=10070)
            if ret is not None:
                self.profile(str(enabledProfiles[0][ret]))
            return
        if mode == '0' or mode == '1' or mode == '2' or mode == '3' or mode == '4':
            if self.check(mode) is False:
                return
            if mode == '0':
                self.toggle(mode)
            else:
                self.profile(mode)
            return
        notify.logError('Wrong arg, use like RunScript("' + ADDON_ID + ',x") x - number of profile')


    def getEnabledProfiles(self):
        enabledProfileKey = []
        enabledProfileName = []
        for k, p in sProfile.items():
            if 'true' in p:
                enabledProfileKey.append(k)
                enabledProfileName.append(sName[k])
        return [enabledProfileKey, enabledProfileName]


    def save(self):
        # get audio config and save to file
        enabledProfiles = self.getEnabledProfiles()
        ret = dialog.DIALOG().start(self.xmlFile, labels={10071: ADDON_LANG(32100)}, buttons=enabledProfiles[1],
                                    thelist=10070)
        if ret is None:
            return False
        else:
            button = enabledProfiles[0][ret]
        settingsToSave = {}
        json_s = [
                # get all settings from System / Audio section
                '{"jsonrpc":"2.0","method":"Settings.GetSettings", "params":{"level": "expert", "filter":{"section":"system","category":"audio"}},"id":1}',
                # get volume level
                '{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["volume"]}, "id": 1}',
                # get all settings from Video / Playback section
                '{"jsonrpc":"2.0","method":"Settings.GetSettings", "params":{"level": "expert", "filter":{"section":"player","category":"videoplayer"}}, "id":1}',
                # get all settings from System / Video section
                '{"jsonrpc":"2.0","method":"Settings.GetSettings", "params":{"level": "expert", "filter":{"section":"system","category":"display"}}, "id":1}'
                 ]
        # send json requests
        for j in json_s:
            jsonGet = xbmc.executeJSONRPC(j)
            jsonGet = json.loads(jsonGet)
            notify.logDebug('[JSON]: ' + str(jsonGet))

            if 'result' in jsonGet:
                if 'settings' in jsonGet['result']:
                    for theset in jsonGet['result']['settings']:
                        if 'value' in theset.keys():

                            if theset['value'] == True or theset['value'] == False:  # lowercase bolean values
                                settingsToSave[theset['id']] = str(theset['value']).lower()
                            else:
                                if isinstance(theset['value'],int):
                                    settingsToSave[theset['id']] = str(theset['value'])
                                else:
                                    settingsToSave[theset['id']] = str(theset['value']).encode('utf-8')

                if 'volume' in jsonGet['result']:
                    settingsToSave['volume'] = str(jsonGet['result']['volume'])
        # prepare JSON string to save to file
        if xbmc_version > 18:
            settingsToSave = convert(settingsToSave)
        jsonToWrite = json.dumps(settingsToSave)
        # create dir in addon data if not exist
        if not xbmcvfs.exists(ADDON_PATH_DATA):
            xbmcvfs.mkdir(ADDON_PATH_DATA)
        # save profile file
        notify.logNotice('[SAVING SETTING]: ' + sName[button])
        f = xbmcvfs.File(os.path.join(ADDON_PATH_DATA,'profile' + str(button) + '.json'), 'w')
        f.write(jsonToWrite)
        f.close()
        notify.popup(ADDON_LANG(32102) + ' ' + str(button) + ' (' + sName[button] + ')')


    def check(self, mode):
        # check profile config
        self.aProfile = []
        # stop if selected (mode) profile are disabled
        if mode != '0' and 'false' in sProfile[int(mode)]:
            notify.popup(ADDON_LANG(32103) + ' (' + sName[int(mode)] + ')')
            notify.logNotice('[CHECK]: This profile is disabled in addon settings - ' + str(mode))
            return False
        # check if profile have settings file
        for key in sProfile:
            if 'true' in sProfile[key]:
                if not xbmcvfs.exists(ADDON_PATH_DATA + 'profile' + str(key) + '.json'):
                    notify.popup(ADDON_LANG(32101) + ' ' + str(key) + ' (' + sName[key] + ')')
                    notify.logError('[PROFILE FILE]: not exist for profile - ' + str(key))
                    return False
                self.aProfile.append(str(key))


    def toggle(self, mode):
        # create profile file
        if not xbmcvfs.exists(ADDON_PATH_DATA):
            xbmcvfs.mkdir(ADDON_PATH_DATA)
        # try read last active profile
        try:
            f = xbmcvfs.File(ADDON_PATH_DATA + 'profile')
            profile = f.read()
            f.close()
            if (len(self.aProfile) == 1) or (profile not in self.aProfile):
                profile = self.aProfile[0]
            else:
                ip = int(self.aProfile.index(profile))
                if len(self.aProfile) == ip:
                    profile = self.aProfile[0]
                else:
                    profile = self.aProfile[ip + 1]
        except (IOError, IndexError):
            profile = self.aProfile[0]
        self.profile(profile)


    def profile(self, profile):
        # read addon settings
        sVolume = ADDON.getSetting('volume')
        sPlayer = ADDON.getSetting('player')
        sVideo = ADDON.getSetting('video')
        sCec = ADDON.getSetting('profile' + profile + '_cec')
        # read settings from profile
        f = xbmcvfs.File(os.path.join(ADDON_PATH_DATA, 'profile' + profile + '.json'), 'r')
        result = f.read()
        try:
            jsonResult = json.loads(result)
            f.close()
        except ValueError:
            notify.popup(ADDON_LANG(32104) + ' ' + profile + ' (' + sName[int(profile)] + ')')
            notify.logError('[LOAD JSON FROM FILE]: Error reading from profile - ' + str(profile))
            return False
        # settings needed quote for value
        quote_needed = [
            'audiooutput.audiodevice',
            'audiooutput.passthroughdevice',
            'locale.audiolanguage',
            'lookandfeel.soundskin'
        ]
        # set settings readed from profile file
        notify.logNotice('[RESTORING SETTING]: ' + sName[int(profile)])
        for setName, setValue in jsonResult.items():
            # skip setting that type is disable to changing
            if 'false' in sPlayer and setName.startswith('videoplayer'):
                continue
            if 'false' in sVideo and setName.startswith('videoscreen'):
                continue
            notify.logDebug('[RESTORING SETTING]: ' + setName + ': ' + setValue)
            # add quotes
            if setName in quote_needed:
                setValue = '"' + setValue + '"'
            # set setting
            if 'true' in sVolume and setName == 'volume':
                xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "Application.SetVolume", "params": {"volume": ' + jsonResult[
                        'volume'] + '}, "id": 1}')
            else:
                xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "Settings.SetSettingValue", "params": {"setting": "' + setName + '", "value": ' + setValue + '}, "id": 1}')
        notify.popup(sName[int(profile)])
        # write curent profile
        f = xbmcvfs.File(os.path.join(ADDON_PATH_DATA, 'profile'), 'w')
        f.write(profile)
        f.close()
        # CEC
        if sCec != '' and int(sCec) > 0:
            notify.logNotice('[SENDING CEC COMMAND]: ' + cecCommands[int(sCec)])
            xbmc.executebuiltin(cecCommands[int(sCec)])
