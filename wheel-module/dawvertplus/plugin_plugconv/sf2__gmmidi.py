# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dawvertplus.plugin_plugconv import base

from dawvertplus.functions import plugins
from dawvertplus.functions import data_bytes

class plugconv(base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['midi', None, None], ['soundfont2', None, None], False, True
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        if 'soundfont' in extra_json:
            print('[plug-conv] MIDI to SoundFont2:',pluginid)
            sffile = extra_json['soundfont']
            v_bank = cvpj_plugindata.dataval_get('bank', 0)
            v_inst = cvpj_plugindata.dataval_get('inst', 0)
            cvpj_plugindata.replace('soundfont2', None)
            cvpj_plugindata.dataval_add('bank', v_bank)
            cvpj_plugindata.dataval_add('patch', v_inst)
            cvpj_plugindata.dataval_add('file', sffile)
            return 1
        print('[plug-conv] No Soundfont Argument Defined:',pluginid)
        return 2