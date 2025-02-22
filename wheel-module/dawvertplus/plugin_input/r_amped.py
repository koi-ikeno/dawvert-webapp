# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
"""
from dawvertplus.functions import data_bytes
from dawvertplus.functions import song
from dawvertplus.functions import colors
from dawvertplus.functions import note_data
from dawvertplus.functions import plugins
from dawvertplus.functions import notelist_data
from dawvertplus.functions import placement_data
from dawvertplus.functions import data_dataset
from dawvertplus.functions import data_values
from dawvertplus.functions import xtramath
from dawvertplus.functions import audio_wav
from dawvertplus.functions_tracks import auto_data
from dawvertplus.functions_tracks import auto_nopl
from dawvertplus.functions_tracks import fxslot
from dawvertplus.functions_tracks import trackfx
from dawvertplus.functions_tracks import tracks_master
from dawvertplus.functions_tracks import tracks_r
import xml.etree.ElementTree as ET
import plugin_input
import json
import os
import struct
import rpp
import base64
import zipfile

amped_colors = {
                'mint': [0.20, 0.80, 0.63],
                'lime': [0.54, 0.92, 0.16],
                'yellow': [0.97, 0.91, 0.11],
                'amber': [1.00, 0.76, 0.33],
                'orange': [0.98, 0.61, 0.38],
                'red': [0.96, 0.38, 0.43],
                'magenta': [0.87, 0.44, 0.96],
                'purple': [0.64, 0.48, 0.96],
                'blue': [0.13, 0.51, 0.96],
                'cyan': [0.20, 0.80, 0.63]
                }

def get_dev_auto(amped_autodata, devid, paramsdata): 
    out = []
    if devid in amped_autodata:
        devauto = amped_autodata[devid]
        for param in paramsdata:
            if 'name' in param:
                if param['name'] in devauto:
                    out.append([param['name'], devauto[param['name']]])
    return out

def eq_calc_q(band_type, q_val):
    if band_type in ['low_pass', 'high_pass']: q_val = xtramath.logpowmul(q_val, 2) if q_val != 0 else 1
    if band_type in ['peak']: q_val = xtramath.logpowmul(q_val, -1) if q_val != 0 else 1
    return q_val

def getsamplefile(filename):
    localpath = os.path.join(projpath, filename)
    if os.path.exists(filename): return filename
    else: return localpath

def do_idparams(paramsdata, device_plugindata, pluginname):
    for param in paramsdata:
        device_plugindata.param_add_dset(param['name'], param['value'], dataset, 'plugin', pluginname)

def do_idauto(amped_autodata, devid, amped_auto, pluginid):
    for s_amped_auto in get_dev_auto(amped_autodata, devid, amped_auto):
        autopoints = auto_nopl.to_pl(s_amped_auto[1])
        auto_data.add_pl(cvpj_l, 'float', ['plugin',pluginid,s_amped_auto[0].replace('/', '__')], autopoints)

def get_contentGuid(contentGuid):
    if isinstance(contentGuid, dict):
        return os.path.join(samplefolder,amped_filenames[str(contentGuid['userAudio']['exportedId'])])
    else:
        return contentGuid

def encode_devices(amped_tr_devices, trackid, amped_autodata):
    for amped_tr_device in amped_tr_devices:
        devid = amped_tr_device['id']
        pluginid = str(devid)
        devicetype = [amped_tr_device['className'], amped_tr_device['label']]

        is_instrument = False

        if devicetype[0] == 'WAM' and devicetype[1] in ['Augur', 'OBXD', 'Dexed']: 
            is_instrument = True
            device_plugindata = plugins.cvpj_plugin('deftype', 'native-amped', devicetype[1])
            device_plugindata.dataval_add('data', amped_tr_device['wamPreset'])
            device_plugindata.to_cvpj(cvpj_l, pluginid)

        elif devicetype[0] == 'WAM' and devicetype[1] == 'Europa': 
            is_instrument = True
            device_plugindata = plugins.cvpj_plugin('deftype', 'synth-nonfree', 'Europa')
            wampreset = amped_tr_device['wamPreset']
            wampreset = json.loads(wampreset)
            europa_xml = ET.fromstring(wampreset['settings'])
            europa_xml_prop = europa_xml.findall('Properties')[0]

            europa_params = {}

            for xmlsub in europa_xml_prop:
                if xmlsub.tag == 'Object':
                    object_name = xmlsub.get('name')
                    for objsub in xmlsub:
                        if objsub.tag == 'Value':
                            value_name = objsub.get('property')
                            value_type = objsub.get('type')
                            value_value = float(objsub.text) if value_type == 'number' else objsub.text
                            europa_params[value_name] = [value_type, value_value]

            paramlist = dataset_synth_nonfree.params_list('plugin', 'europa')
            for paramname in paramlist:
                dset_paramdata = dataset_synth_nonfree.params_i_get('plugin', 'europa', paramname)
                if dset_paramdata[5] in europa_params:
                    s_paramdata = europa_params[dset_paramdata[5]]

                    if s_paramdata[0] == 'number': 
                        device_plugindata.param_add_dset(paramname, s_paramdata[1], dataset_synth_nonfree, 'plugin', 'europa')
                    else:
                        if value_name in ['Curve1','Curve2','Curve3','Curve4','Curve']: value_value = list(bytes.fromhex(value_value))
                        device_plugindata.dataval_add(paramname, s_paramdata[1])

            if 'encodedSampleData' in wampreset:
                europa_sampledata = wampreset['encodedSampleData']
                device_plugindata.dataval_add('encodedSampleData', europa_sampledata)
            device_plugindata.to_cvpj(cvpj_l, pluginid)

        elif devicetype[0] == 'WAM' and devicetype[1] in ['Amp Sim Utility']: 
            device_plugindata = plugins.cvpj_plugin('deftype', 'native-amped', devicetype[1])
            device_plugindata.dataval_add('data', amped_tr_device['wamPreset'])
            device_plugindata.to_cvpj(cvpj_l, pluginid)

        elif devicetype == ['Drumpler', 'Drumpler']:
            is_instrument = True
            device_plugindata = plugins.cvpj_plugin('deftype', 'native-amped', 'Drumpler')
            device_plugindata.dataval_add('kit', amped_tr_device['kit'])
            do_idparams(amped_tr_device['params'], device_plugindata, devicetype[0])
            device_plugindata.to_cvpj(cvpj_l, pluginid)

        elif devicetype == ['SF2', 'GM Player']:
            is_instrument = True
            value_patch = 0
            value_bank = 0
            value_gain = 0.75
            for param in amped_tr_device['params']:
                paramname, paramval = param['name'], param['value']
                if paramname == 'patch': value_patch = paramval
                if paramname == 'bank': value_bank = paramval
                if paramname == 'gain': value_gain = paramval
            device_plugindata = plugins.cvpj_plugin('midi', value_bank, value_patch)
            device_plugindata.param_add('gain', paramval, 'float', 'Gain')
            device_plugindata.to_cvpj(cvpj_l, pluginid)

        elif devicetype == ['Granny', 'Granny']:
            is_instrument = True
            device_plugindata = plugins.cvpj_plugin('deftype', 'native-amped', 'Granny')
            do_idparams(amped_tr_device['params'], device_plugindata, devicetype[0])
            device_plugindata.dataval_add('grannySampleGuid', amped_tr_device['grannySampleGuid'])
            device_plugindata.dataval_add('grannySampleName', amped_tr_device['grannySampleName'])
            device_plugindata.to_cvpj(cvpj_l, pluginid)
            do_idauto(amped_autodata, devid, amped_tr_device['params'], pluginid)

        elif devicetype == ['Volt', 'VOLT']:
            is_instrument = True
            device_plugindata = plugins.cvpj_plugin('deftype', 'native-amped', 'Volt')
            do_idparams(amped_tr_device['params'], device_plugindata, devicetype[0])
            device_plugindata.to_cvpj(cvpj_l, pluginid)
            do_idauto(amped_autodata, devid, amped_tr_device['params'], pluginid)

        elif devicetype == ['VoltMini', 'VOLT Mini']:
            is_instrument = True
            device_plugindata = plugins.cvpj_plugin('deftype', 'native-amped', 'VoltMini')
            do_idparams(amped_tr_device['params'], device_plugindata, devicetype[0])
            device_plugindata.to_cvpj(cvpj_l, pluginid)
            do_idauto(amped_autodata, devid, amped_tr_device['params'], pluginid)

        elif devicetype == ['Sampler', 'Sampler']:
            is_instrument = True
            samplerdata = {}
            for param in amped_tr_device['params']:
                data_values.nested_dict_add_value(samplerdata, param['name'].split('/'), param['value'])

            amped_tr_device['zonefile'] = {}
            for param in amped_tr_device['samplerZones']:
                amped_tr_device['zonefile'][str(param['id'])] = param['contentGuid']

            device_plugindata = plugins.cvpj_plugin('multisampler', None, None)
            device_plugindata.dataval_add('point_value_type', "percent")

            samplerdata_voiceLimit = samplerdata['voiceLimit']
            samplerdata_filter = samplerdata['filter']
            samplerdata_eg = samplerdata['eg']
            samplerdata_zone = samplerdata['zone']
            samplerdata_zonefile = amped_tr_device['zonefile']
            
            for samplerdata_zp in samplerdata_zone:
                amped_samp_part = samplerdata_zone[samplerdata_zp]
                cvpj_region = {}
                cvpj_region['file'] = get_contentGuid(samplerdata_zonefile[samplerdata_zp])
                cvpj_region['reverse'] = 0
                cvpj_region['loop'] = {}
                cvpj_region['loop']['enabled'] = 0
                cvpj_region['loop']['points'] = [amped_samp_part['looping']['startPositionNorm'], amped_samp_part['looping']['endPositionNorm']]
                cvpj_region['middlenote'] = amped_samp_part['key']['root']-60
                cvpj_region['r_key'] = [int(amped_samp_part['key']['min'])-60, int(amped_samp_part['key']['max'])-60]
                device_plugindata.region_add(cvpj_region)

            device_plugindata.to_cvpj(cvpj_l, pluginid)

        elif devicetype == ['EqualizerPro', 'Equalizer']:
            device_plugindata = plugins.cvpj_plugin('deftype', 'native-amped', 'EqualizerPro')
            do_idparams(amped_tr_device['params'], device_plugindata, devicetype[0])
            device_plugindata.to_cvpj(cvpj_l, pluginid)
            do_idauto(amped_autodata, devid, amped_tr_device['params'], pluginid)

        elif devicetype[0] in ['Chorus',  
        'CompressorMini', 'Delay', 'Distortion', 'Equalizer', 
        'Flanger', 'Gate', 'Limiter', 'LimiterMini', 'Phaser', 
        'Reverb', 'Tremolo', 'BitCrusher', 'Tremolo', 'Vibrato', 'Compressor', 'Expander']:
            device_plugindata = plugins.cvpj_plugin('deftype', 'native-amped', devicetype[0])
            do_idparams(amped_tr_device['params'], device_plugindata, devicetype[0])
            device_plugindata.to_cvpj(cvpj_l, pluginid)
            do_idauto(amped_autodata, devid, amped_tr_device['params'], pluginid)


        #if devicetype != ['VSTConnection', 'VST/Remote Beta']:
        #    device_plugindata.fxvisual_add(devicetype[1], None)
        #    device_plugindata.to_cvpj(cvpj_l, pluginid)

        if is_instrument == True: tracks_r.track_inst_pluginid(cvpj_l, trackid, pluginid)
        else:
            if trackid == None: fxslot.insert(cvpj_l, ['master'], 'audio', pluginid)
            else: fxslot.insert(cvpj_l, ['track', trackid], 'audio', pluginid)

def ampedauto_to_cvpjauto_specs(autopoints, autospecs):
    v_min = 0
    v_max = 1
    if autospecs['type'] == 'numeric':
        v_min = autospecs['min']
        v_max = autospecs['max']

    ampedauto = []
    for autopoint in autopoints:
        ampedauto.append({
            "position": autopoint['pos']*4, 
            "value": xtramath.between_from_one(v_min, v_max, autopoint['value'])
            })
    return ampedauto

def ampedauto_to_cvpjauto(autopoints):
    ampedauto = []
    for autopoint in autopoints:
        ampedauto.append({"position": autopoint['pos']*4, "value": autopoint['value']})
    return ampedauto

class input_amped(base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'amped'
    def getname(self): return 'Amped Studio'
    def gettype(self): return 'r'
    def supported_autodetect(self): return True
    def detect(self, input_file): 
        try:
            zip_data = zipfile.ZipFile(input_file, 'r')
            if 'amped-studio-project.json' in zip_data.namelist(): return True
            else: return False
        except:
            return False
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': [],
        'track_hybrid': True,
        'placement_audio_stretch': ['rate'],
        'placement_audio_nested': True
        }
    def parse(self, input_file, extra_param):
        global cvpj_l
        global samplefolder
        global amped_filenames
        global europa_vals
        global dataset
        global dataset_synth_nonfree

        dataset = data_dataset.dataset('./data_dset/amped.dset')
        dataset_synth_nonfree = data_dataset.dataset('./data_dset/synth_nonfree.dset')

        cvpj_l = {}
        samplefolder = extra_param['samplefolder']
        zip_data = zipfile.ZipFile(input_file, 'r')
        amped_project = json.loads(zip_data.read('amped-studio-project.json'))
        amped_filenames = json.loads(zip_data.read('filenames.json'))

        amped_tracks = amped_project['tracks']
        amped_masterTrack = amped_project['masterTrack']
        #encode_devices(amped_masterTrack['devices'], None)
        amped_looping = amped_project['looping']
        amped_tempo = amped_project['tempo']
        amped_timeSignature = amped_project['timeSignature']

        song.add_param(cvpj_l, 'bpm', amped_tempo)
        song.add_timesig(cvpj_l, amped_timeSignature['num'], amped_timeSignature['den'])

        for amped_filename in amped_filenames:
            realfilename = amped_filenames[amped_filename]
            old_file = os.path.join(samplefolder,amped_filename)
            new_file = os.path.join(samplefolder,realfilename)
            if os.path.exists(new_file) == False:
                zip_data.extract(amped_filename, path=samplefolder, pwd=None)
                os.rename(old_file,new_file)

        for amped_track in amped_tracks:
            amped_tr_id = str(amped_track['id'])
            amped_tr_name = amped_track['name']
            amped_tr_color = amped_track['color'] if 'color' in amped_track else 'lime'
            amped_tr_pan = amped_track['pan']
            amped_tr_volume = amped_track['volume']
            amped_tr_mute = amped_track['mute']
            amped_tr_solo = amped_track['solo']
            amped_tr_regions = amped_track['regions']
            amped_tr_devices = amped_track['devices']
            amped_tr_automations = amped_track['automations']

            for amped_tr_automation in amped_tr_automations:
                autoname = amped_tr_automation['param']
                autopoints = auto_nopl.to_pl(ampedauto_to_cvpjauto(amped_tr_automation['points']))
                if autoname == 'volume': auto_data.add_pl(cvpj_l, 'float', ['track',amped_tr_id,'vol'], autopoints)
                if autoname == 'pan': auto_data.add_pl(cvpj_l, 'float', ['track',amped_tr_id,'pan'], autopoints)
                
            tracks_r.track_create(cvpj_l, amped_tr_id, 'hybrid')
            tracks_r.track_visual(cvpj_l, amped_tr_id, name=amped_tr_name, color=amped_colors[amped_tr_color])
            tracks_r.track_param_add(cvpj_l, amped_tr_id, 'vol', amped_tr_volume, 'float')
            tracks_r.track_param_add(cvpj_l, amped_tr_id, 'pan', amped_tr_pan, 'float')
            tracks_r.track_param_add(cvpj_l, amped_tr_id, 'enabled', int(not amped_tr_mute), 'bool')
            tracks_r.track_param_add(cvpj_l, amped_tr_id, 'solo', int(amped_tr_solo), 'bool')

            amped_autodata = {}
            for amped_tr_automation in amped_tr_automations:
                if 'param' in amped_tr_automation:
                    amped_tr_autoparam = amped_tr_automation['param']
                    devid = amped_tr_autoparam['deviceId']
                    autoname = amped_tr_autoparam['name']
                    if devid not in amped_autodata: amped_autodata[devid] = {}
                    amped_autodata[devid][autoname] = ampedauto_to_cvpjauto_specs(amped_tr_automation['points'], amped_tr_automation['spec'])

            encode_devices(amped_tr_devices, amped_tr_id, amped_autodata)
            for amped_reg in amped_tr_regions:
                amped_reg_position = amped_reg['position']*4
                amped_reg_length = amped_reg['length']*4
                amped_reg_offset = amped_reg['offset']*4
                amped_reg_clips = amped_reg['clips']
                amped_reg_midi = amped_reg['midi']
                amped_reg_name = amped_reg['name']
                amped_reg_color = amped_reg['color'] if 'color' in amped_reg else 'lime'
                cvpj_placement_base = {}
                cvpj_placement_base['position'] = amped_reg_position
                cvpj_placement_base['duration'] = amped_reg_length
                cvpj_placement_base['name'] = amped_reg['name']
                cvpj_placement_base['color'] = amped_colors[amped_reg_color]
                cvpj_placement_base['cut'] = {'type': 'cut', 'start':amped_reg_offset, 'end': amped_reg_length+amped_reg_offset}

                if amped_reg_midi != {'notes': [], 'events': [], 'chords': []}: 
                    cvpj_placement_notes = cvpj_placement_base.copy()
                    cvpj_placement_notes['notelist'] = []
                    for amped_note in amped_reg_midi['notes']:
                        cvpj_note = note_data.rx_makenote(amped_note['position']*4, amped_note['length']*4, amped_note['key']-60,  amped_note['velocity']/127, None)
                        cvpj_placement_notes['notelist'].append(cvpj_note)
                    tracks_r.add_pl(cvpj_l, amped_tr_id, 'notes', cvpj_placement_notes)

                if amped_reg_clips != []:
                    cvpj_placement_audionested = cvpj_placement_base.copy()
                    clip_events = []

                    for amped_reg_clip in amped_reg_clips:
                        temp_pl = {}
                        temp_pl['file'] = get_contentGuid(amped_reg_clip['contentGuid'])
                        temp_pl['position'] = (amped_reg_clip['position']*4)
                        temp_pl['duration'] = (amped_reg_clip['length']*4)
                        temp_pl['vol'] = amped_reg_clip['gain']
                        temp_pl['audiomod'] = {}
                        temp_pl['audiomod']['stretch_algorithm'] = 'stretch'
                        temp_pl['audiomod']['stretch_method'] = 'rate_speed'
                        temp_pl['audiomod']['stretch_data'] = {'rate': 1/amped_reg_clip['stretch']}

                        amped_reg_clip_offset = amped_reg_clip['offset']*4
                        if amped_reg_clip_offset != 0:
                            temp_pl['cut'] = {'type': 'cut', 'start':amped_reg_clip_offset}
                        clip_events.append(temp_pl)

                    cvpj_placement_audionested['events'] = clip_events
                    tracks_r.add_pl(cvpj_l, amped_tr_id, 'audio_nested', cvpj_placement_audionested)



        return json.dumps(cvpj_l)
"""