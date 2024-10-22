# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dawvertplus.functions import data_values
from dawvertplus.functions import auto
#from dawvertplus.functions import params

def add_pl(cvpj_l, val_type, autolocation, in_autopoints):
    if autolocation != None:
        data_values.nested_dict_add_value(cvpj_l, ['automation']+autolocation+['type'], val_type)
        data_values.nested_dict_add_to_list(cvpj_l, ['automation']+autolocation+['placements'], in_autopoints)

def iter(cvpj_l):
    outdata = []
    if 'automation' in cvpj_l:
        cvpj_auto = cvpj_l['automation']
        for autotype in cvpj_auto:
            if autotype in ['main', 'master']:
                for autovarname in cvpj_auto[autotype]:
                    outdata.append([False, [autotype, autovarname], cvpj_auto[autotype][autovarname]])
            else:
                for autonameid in cvpj_auto[autotype]:
                    for autovarname in cvpj_auto[autotype][autonameid]:
                        outdata.append([True, [autotype, autonameid, autovarname], cvpj_auto[autotype][autonameid][autovarname]])
    return outdata

def move(cvpj_l, old_autolocation, new_autolocation):
    print('[tracks] Moving Automation:','/'.join(old_autolocation),'to','/'.join(new_autolocation))
    dictvals = data_values.nested_dict_get_value(cvpj_l, ['automation']+old_autolocation)
    if dictvals != None:
        data_values.nested_dict_add_value(cvpj_l, ['automation']+new_autolocation, dictvals)
        if old_autolocation[0] in ['main', 'master']:
            del cvpj_l['automation'][old_autolocation[0]][old_autolocation[1]]
        else:
            del cvpj_l['automation'][old_autolocation[0]][old_autolocation[1]][old_autolocation[2]]

def rename_plugparam(cvpj_l, pluginid, oldname, newname):
    move(cvpj_l, ['plugin', pluginid, oldname], ['plugin', pluginid, newname])

def del_plugin(cvpj_l, pluginid):
    print('[tracks] Removing Plugin Automation:',pluginid)
    dictvals = data_values.nested_dict_get_value(cvpj_l, ['automation', 'plugin', pluginid])
    if dictvals != None: del cvpj_l['automation']['plugin'][pluginid]

def change_valrange(cvpj_l, autolocation, old_min, old_max, new_min, new_max):
    dictvals = data_values.nested_dict_get_value(cvpj_l, ['automation']+autolocation)
    if dictvals != None: 
        if 'placements' in dictvals:
            dictvals = auto.change_valrange(dictvals['placements'], old_min, old_max, new_min, new_max)

def to_one(cvpj_l, autolocation, v_min, v_max):
    dictvals = data_values.nested_dict_get_value(cvpj_l, ['automation']+autolocation)
    if dictvals != None: 
        if 'placements' in dictvals:
            dictvals = auto.to_one(dictvals['placements'], v_min, v_max)

def multiply(cvpj_l, autolocation, addval, mulval):
    dictvals = data_values.nested_dict_get_value(cvpj_l, ['automation']+autolocation)
    if dictvals != None: 
        if 'placements' in dictvals:
            dictvals = auto.multiply(dictvals['placements'], addval, mulval)

def to_ext_one(cvpj_l, pluginid, oldname, newname, v_min, v_max):
    move(cvpj_l, ['plugin', pluginid, oldname], ['plugin', pluginid, newname])
    to_one(cvpj_l, ['plugin', pluginid, newname], v_min, v_max)

def function_value(cvpj_l, autolocation, i_function):
    dictvals = data_values.nested_dict_get_value(cvpj_l, ['automation']+autolocation)
    if dictvals != None: 
        if 'placements' in dictvals:
            for dictval in dictvals['placements']:
                if 'points' in dictval:
                    for point in dictval['points']:
                        point['value'] = i_function(point['value'])


