# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dawvertplus.functions import note_data
from dawvertplus.functions import placement_data
from dawvertplus.functions import plugins
from dawvertplus.functions import song
from dawvertplus.functions import colors
from dawvertplus.functions import data_dataset
from dawvertplus.functions_tracks import fxslot
from dawvertplus.functions_tracks import trackfx
from dawvertplus.functions_tracks import tracks_master
from dawvertplus.functions_tracks import tracks_r
import json
from dawvertplus.plugin_input import base
import xml.etree.ElementTree as ET
import zipfile

def getvalue(xmltag, xmlname, fallbackval): 
    if xmltag.findall(xmlname) != []: return xmltag.findall(xmlname)[0].text.strip()
    else: return fallbackval

def getbool(input_val):
    if input_val == 'true': return 1
    if input_val == 'false': return 0

def setasdr(i_attack, i_decay, i_release, i_sustain):
    out_attack = i_attack
    out_decay = i_decay
    out_release = i_release
    out_sustain = i_sustain
    if out_decay == 0: i_sustain = 1
    return out_attack, out_decay, out_release, out_sustain

audiosanua_device_id = ['fm', 'analog']

def make_fxslot(x_device_sound, fx_type, as_device):
    pluginid = plugins.get_id()

    fx_wet = 1
    if fx_type == 'chorus':
        fx_plugindata = plugins.cvpj_plugin('deftype', 'native-audiosauna', 'chorus')
        fx_plugindata.param_add("speed", float(getvalue(x_device_sound, 'chorusSpeed', 0))/100, 'float', "Speed")

        if as_device in [0,1]: 
            fx_wet = float(getvalue(x_device_sound, 'chorusMix', 0))/100
            fx_plugindata.param_add("size", float(getvalue(x_device_sound, 'chorusLevel', 0))/100, 'float', "Size")
        else: 
            fx_wet = float(getvalue(x_device_sound, 'chorusDryWet', 0))/100
            fx_plugindata.param_add("size", float(getvalue(x_device_sound, 'chorusSize', 0))/100, 'float', "Size")

        fx_plugindata.fxdata_add(True, fx_wet)
        fx_plugindata.fxvisual_add('Chorus', None)
        fx_plugindata.to_cvpj(cvpj_l, pluginid)

    if fx_type == 'distortion':
        fx_plugindata = plugins.cvpj_plugin('deftype', 'native-audiosauna', 'distortion')
        fx_plugindata.param_add("overdrive", float(getvalue(x_device_sound, 'overdrive', 0))/100, 'float', "Overdrive")
        if as_device in [0,1]: fx_plugindata.param_add("modulate", float(getvalue(x_device_sound, 'driveModul', 0))/100, 'float', "Modulate")
        else: fx_plugindata.param_add("modulate", float(getvalue(x_device_sound, 'modulate', 0))/100, 'float', "Modulate")
        fx_plugindata.fxvisual_add('Distortion', None)
        fx_plugindata.to_cvpj(cvpj_l, pluginid)

    if fx_type == 'bitcrush':
        bitrateval = float(getvalue(x_device_sound, 'bitrate', 0))
        if bitrateval != 0.0: 
            fx_plugindata = plugins.cvpj_plugin('deftype', 'native-audiosauna', 'bitcrush')
            fx_plugindata.param_add("frames", bitrateval, 'float', "Frames")
            fx_plugindata.fxvisual_add('Bitcrush', None)
            fx_plugindata.to_cvpj(cvpj_l, pluginid)

    if fx_type == 'tape_delay':
        fx_plugindata = plugins.cvpj_plugin('deftype', 'native-audiosauna', 'tape_delay')
        fx_plugindata.param_add("time", float(getvalue(x_device_sound, 'dlyTime', 0)), 'float', "Time")
        fx_plugindata.param_add("damage", float(getvalue(x_device_sound, 'dlyDamage', 0))/100, 'float', "Damage")
        fx_plugindata.param_add("feedback", float(getvalue(x_device_sound, 'dlyFeed', 0))/100, 'float', "Feedback")
        fx_plugindata.param_add("sync", getbool(getvalue(x_device_sound, 'dlySync', 0)), 'float', "Sync")
        fx_plugindata.fxvisual_add('Tape Delay', None)
        fx_plugindata.to_cvpj(cvpj_l, pluginid)

    if fx_type == 'reverb':
        fx_plugindata = plugins.cvpj_plugin('deftype', 'native-audiosauna', 'reverb')
        fx_plugindata.param_add("time", float(getvalue(x_device_sound, 'rvbTime', 0)), 'float', "Time")
        fx_plugindata.param_add("feedback", float(getvalue(x_device_sound, 'rvbFeed', 0))/100, 'float', "Feedback")
        fx_plugindata.param_add("width", float(getvalue(x_device_sound, 'rvbWidth', 0))/100, 'float', "Width")
        fx_plugindata.fxvisual_add('Reverb', None)
        fx_plugindata.to_cvpj(cvpj_l, pluginid)

    if fx_type == 'amp':
        ampval = float(getvalue(x_device_sound, 'masterAmp', 0))/100
        if ampval != 1.0: 
            fx_plugindata = plugins.cvpj_plugin('deftype', 'native-audiosauna', 'amp')
            fx_plugindata.param_add("level", ampval, 'float', "Level")
            fx_plugindata.fxvisual_add('Amp', None)
            fx_plugindata.to_cvpj(cvpj_l, pluginid)
        
    return pluginid

class input_audiosanua(base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'audiosauna'
    def getname(self): return 'AudioSauna'
    def gettype(self): return 'r'
    def getdawcapabilities(self): return {'placement_cut': True}
    def supported_autodetect(self): return True
    def detect(self, input_file): 
        try:
            zip_data = zipfile.ZipFile(input_file, 'r')
            if 'songdata.xml' in zip_data.namelist(): return True
            else: return False
        except:
            return False
    def parse(self, input_file, extra_param):
        global cvpj_l
        zip_data = zipfile.ZipFile(input_file, 'r')

        cvpj_l = {}

        dataset = data_dataset.dataset('./data_dset/audiosauna.dset')
        colordata = colors.colorset(dataset.colorset_e_list('track', 'main'))

        songdataxml_filename = None

        t_audiosanua_project = zip_data.read('songdata.xml')

        x_proj = ET.fromstring(t_audiosanua_project)

        x_proj_channels = x_proj.findall('channels')[0]
        x_proj_tracks = x_proj.findall('tracks')[0]
        x_proj_songPatterns = x_proj.findall('songPatterns')[0]
        x_proj_devices = x_proj.findall('devices')[0]

        xt_chan = x_proj_channels.findall('channel')
        xt_track = x_proj_tracks.findall('track')
        xt_pattern = x_proj_songPatterns.findall('pattern')
        xt_devices = x_proj_devices.findall('audioDevice')

        x_BPM = float(getvalue(x_proj, 'appTempo', 170))

        cvpj_plnotes = {}
        as_patt_notes = {}

        tracks_master.create(cvpj_l, int(getvalue(x_proj,'appMasterVolume',100))/100)
        tracks_master.visual(cvpj_l, name='Master')


        trackfx.return_add(cvpj_l, ['master'], 'audiosauna_send_tape_delay')
        trackfx.return_visual(cvpj_l, ['master'], 'audiosauna_send_tape_delay', name='Tape Delay')
        trackfx.return_param_add(cvpj_l, ['master'], 'audiosauna_send_tape_delay', 'vol', int(getvalue(x_proj,'dlyLevel',100))/100, 'float')
        fxslot.insert(cvpj_l, ['return', None, 'audiosauna_send_tape_delay'], 'audio', make_fxslot(x_proj, 'tape_delay', None))

        trackfx.return_add(cvpj_l, ['master'], 'audiosauna_send_reverb')
        trackfx.return_visual(cvpj_l, ['master'], 'audiosauna_send_reverb', name='Reverb')
        trackfx.return_param_add(cvpj_l, ['master'], 'audiosauna_send_reverb', 'vol', int(getvalue(x_proj,'rvbLevel',100))/100, 'float')
        fxslot.insert(cvpj_l, ['return', None, 'audiosauna_send_reverb'], 'audio', make_fxslot(x_proj, 'reverb', None))

        # ------------------------------------------ tracks ------------------------------------------
        for x_track in xt_track:
            x_track_trackIndex = int(x_track.get('trackIndex'))
            xt_track_seqNote = x_track.findall('seqNote')
            for x_track_seqNote in xt_track_seqNote:
                as_note_patternId = int(x_track_seqNote.get('patternId'))
                as_note_startTick = int(x_track_seqNote.get('startTick'))
                as_note_endTick = int(x_track_seqNote.get('endTick'))
                as_note_noteLength = int(x_track_seqNote.get('noteLength'))
                as_note_pitch = int(x_track_seqNote.get('pitch'))
                as_note_noteVolume = int(x_track_seqNote.get('noteVolume'))
                as_note_noteCutoff = int(x_track_seqNote.get('noteCutoff'))
                if as_note_patternId not in as_patt_notes: as_patt_notes[as_note_patternId] = []
                as_patt_notes[as_note_patternId].append([as_note_startTick, as_note_endTick, as_note_noteLength, as_note_pitch, as_note_noteVolume, as_note_noteCutoff])

        # ------------------------------------------ channels ------------------------------------------
        for x_chan in xt_chan:
            as_channum = int(x_chan.get('channelNro'))
            cvpj_id = 'audiosanua'+str(as_channum)

            cvpj_tr_vol = int(x_chan.get('volume'))/100
            cvpj_tr_pan = int(x_chan.get('pan'))/100
            cvpj_tr_name = x_chan.get('name')
            cvpj_tr_mute = getbool(x_chan.get('mute'))
            cvpj_tr_solo = getbool(x_chan.get('solo'))

            cvpj_tr_color = colordata.getcolornum(as_channum)

            tracks_r.track_create(cvpj_l, cvpj_id, 'instrument')
            tracks_r.track_visual(cvpj_l, cvpj_id, name=cvpj_tr_name, color=cvpj_tr_color)

            tracks_r.track_param_add(cvpj_l, cvpj_id, 'vol', cvpj_tr_vol, 'float')
            tracks_r.track_param_add(cvpj_l, cvpj_id, 'pan', cvpj_tr_pan, 'float')
            tracks_r.track_param_add(cvpj_l, cvpj_id, 'enabled', int(not getbool(x_chan.get('mute'))), 'bool')
            tracks_r.track_param_add(cvpj_l, cvpj_id, 'solo', getbool(x_chan.get('solo')), 'bool')
            trackfx.send_add(cvpj_l, cvpj_id, 'audiosauna_send_tape_delay', int(x_chan.get('delay'))/100, None)
            trackfx.send_add(cvpj_l, cvpj_id, 'audiosauna_send_reverb', int(x_chan.get('reverb'))/100, None)

        # ------------------------------------------ patterns ------------------------------------------
        for x_pattern in xt_pattern:
            as_pattern_trackNro = int(x_pattern.get('trackNro'))
            as_pattern_patternId = int(x_pattern.get('patternId'))
            as_pattern_patternColor = int(x_pattern.get('patternColor'))
            as_pattern_startTick = int(x_pattern.get('startTick'))
            as_pattern_endTick = int(x_pattern.get('endTick'))
            as_pattern_patternLength = int(x_pattern.get('patternLength'))

            cvpj_pldata = placement_data.makepl_n(as_pattern_startTick/32, (as_pattern_endTick-as_pattern_startTick)/32, [])
            cvpj_pldata['cut'] = {'type': 'cut', 'start': 0, 'end': as_pattern_patternLength/32}
            plcolor = colordata.getcolornum(as_pattern_patternColor)
            if plcolor: cvpj_pldata['color'] = plcolor

            if as_pattern_patternId in as_patt_notes:
                t_notelist = as_patt_notes[as_pattern_patternId]
                for t_note in t_notelist:
                    cvpj_note = note_data.rx_makenote((max(0,t_note[0]-as_pattern_startTick)/32), t_note[2]/32, t_note[3]-60, t_note[4]/100, None)
                    cvpj_note['cutoff'] = t_note[5]
                    cvpj_pldata['notelist'].append(cvpj_note)

            tracks_r.add_pl(cvpj_l, 'audiosanua'+str(as_pattern_trackNro), 'notes', cvpj_pldata)
        # ------------------------------------------ patterns ------------------------------------------
        devicenum = 0
        for x_device in xt_devices:
            v_device_deviceType = int(x_device.get('deviceType'))
            v_device_visible = x_device.get('visible')
            v_device_xpos = int(x_device.get('xpos'))
            v_device_ypos = int(x_device.get('ypos'))

            cvpj_trackid = 'audiosanua'+str(devicenum)

            pluginid = plugins.get_id()

            song.add_visual_window(cvpj_l, 'plugin', pluginid, [v_device_xpos, v_device_ypos], None, getbool(v_device_visible), False)

            if v_device_deviceType == 1 or v_device_deviceType == 0:
                inst_plugindata = plugins.cvpj_plugin('deftype', 'native-audiosauna', audiosanua_device_id[v_device_deviceType])
                x_device_sound = x_device.findall('sound')[0]

                paramlist = dataset.params_list('plugin', str(v_device_deviceType))
                if paramlist:
                    for paramid in paramlist:
                        inst_plugindata.param_add_dset(paramid, getvalue(x_device_sound, paramid, 0), dataset, 'plugin', str(v_device_deviceType))

                v_attack, v_decay, v_release, v_sustain = setasdr(
                    float(getvalue(x_device_sound, 'attack', 0)), 
                    float(getvalue(x_device_sound, 'decay', 0)), 
                    float(getvalue(x_device_sound, 'release', 0)), 
                    float(getvalue(x_device_sound, 'sustain', 0))
                    )

                inst_plugindata.asdr_env_add('volume', 0, v_attack, 0, v_decay, v_sustain, v_release, 1)

                if v_device_deviceType == 1: oprange = 2
                if v_device_deviceType == 0: oprange = 4
                inst_plugindata.osc_num_oscs(oprange)
                for opnum in range(oprange):
                    opnumtxt = str(opnum+1)

                    op_attack, op_decay, op_release, op_sustain = setasdr(
                        float(getvalue(x_device_sound, 'aOp'+opnumtxt, 0)), 
                        float(getvalue(x_device_sound, 'dOp'+opnumtxt, 0)), 
                        -1, 
                        float(getvalue(x_device_sound, 'sOp'+opnumtxt, 0))/100 )
                    inst_plugindata.asdr_env_add('op'+opnumtxt, 0, op_attack, 0, op_decay, op_sustain, op_release, 1)
                    inst_plugindata.osc_opparam_set(opnum, 'env', {'vol': 'op'+opnumtxt})

                    if v_device_deviceType == 0: 
                        as_oct = int(getvalue(x_device_sound, 'oct'+opnumtxt, 0))*12
                        as_fine = int(getvalue(x_device_sound, 'oct'+opnumtxt, 0))
                        as_semi = int(getvalue(x_device_sound, 'semi'+opnumtxt, 0))
                        as_shape = int(getvalue(x_device_sound, 'wave'+opnumtxt, 0))
                        as_vol = int(getvalue(x_device_sound, 'osc'+opnumtxt+'Vol', 1))

                        inst_plugindata.osc_opparam_set(opnum, 'course', as_oct+as_fine)
                        inst_plugindata.osc_opparam_set(opnum, 'fine', as_semi/100)
                        inst_plugindata.osc_opparam_set(opnum, 'vol', as_vol)

                        if as_shape == 0: inst_plugindata.osc_opparam_set(opnum, 'shape', 'saw')
                        if as_shape == 1: inst_plugindata.osc_opparam_set(opnum, 'shape', 'square')
                        if as_shape == 2: inst_plugindata.osc_opparam_set(opnum, 'shape', 'triangle')
                        if as_shape == 3: inst_plugindata.osc_opparam_set(opnum, 'shape', 'noise')
                        if as_shape == 4: inst_plugindata.osc_opparam_set(opnum, 'shape', 'sine')


            if v_device_deviceType == 2:
                inst_plugindata = plugins.cvpj_plugin('multisampler', None, None)
                inst_plugindata.dataval_add('point_value_type', "percent")
                x_device_sound = x_device.findall('sampler')[0]

                x_device_samples = x_device_sound.findall('samples')[0]
                for x_cell in x_device_samples.findall('cell'):
                    t_loKey = float(getvalue(x_cell, 'loKey', 60))
                    t_hiKey = float(getvalue(x_cell, 'hiKey', 60))
                    t_rootKey = float(getvalue(x_cell, 'rootKey', 60))
                    t_loopMode = getvalue(x_cell, 'loopMode', 'off')
                    t_loopStart = float(getvalue(x_cell, 'loopStart', 0))
                    t_loopEnd = float(getvalue(x_cell, 'loopEnd', 100))
                    t_playMode = getvalue(x_cell, 'playMode', 'forward')
                    t_smpStart = float(getvalue(x_cell, 'smpStart', 0))
                    t_smpEnd = float(getvalue(x_cell, 'smpEnd', 100))

                    cvpj_region = {}
                    cvpj_region['point_value_type'] = 'percent'
                    cvpj_region['name'] = getvalue(x_cell, 'name', '')
                    cvpj_region['file'] = getvalue(x_cell, 'url', '')
                    if t_playMode == 'forward': cvpj_region['reverse'] = 0
                    else: cvpj_region['reverse'] = 1
                    cvpj_region['tone'] = float(getvalue(x_cell, 'semitone', 0))
                    cvpj_region['fine'] = float(getvalue(x_cell, 'finetone', 0))
                    cvpj_region['volume'] = float(getvalue(x_cell, 'volume', 100))/100
                    cvpj_region['pan'] = float(getvalue(x_cell, 'pan', 100))/100
                    cvpj_region['loop'] = {}
                    if t_loopMode == 'off':
                        cvpj_region['loop']['enabled'] = 0
                    if t_loopMode == 'normal':
                        cvpj_region['loop']['enabled'] = 1
                        cvpj_region['loop']['mode'] = 'normal'
                    if t_loopMode == 'ping-pong':
                        cvpj_region['loop']['enabled'] = 1
                        cvpj_region['loop']['mode'] = 'pingpong'
                    cvpj_region['loop']['points'] = [float(t_loopStart)/100, float(t_loopEnd)/100]
                    cvpj_region['middlenote'] = t_rootKey-60
                    cvpj_region['r_key'] = [int(t_loKey)-60, int(t_hiKey)-60]
                    cvpj_region['start'] = float(t_smpStart)/100
                    cvpj_region['end'] = float(t_smpEnd)/100
                    cvpj_region['trigger'] = 'normal'
                    inst_plugindata.region_add(cvpj_region)

                v_attack, v_decay, v_release, v_sustain = setasdr(
                    float(getvalue(x_device_sound, 'masterAttack', 0)), 
                    float(getvalue(x_device_sound, 'masterDecay', 0)), 
                    float(getvalue(x_device_sound, 'masterRelease', 0)), 
                    float(getvalue(x_device_sound, 'masterSustain', 0))
                    )

                inst_plugindata.asdr_env_add('volume', 0, v_attack, 0, v_decay, v_sustain, v_release, 1)

            #cvpj_instdata['middlenote'] = int(getvalue(x_device_sound, 'masterTranspose', 0))*-1

            pre_t_cutoff = int(getvalue(x_device_sound, 'cutoff', 0))/100

            filter_cutoff = int(pre_t_cutoff)*7200
            filter_reso = int(getvalue(x_device_sound, 'resonance', 0))/100

            audiosauna_filtertype = getvalue(x_device_sound, 'filterType', '0')
            if audiosauna_filtertype == '0': filter_type = ['lowpass', None]
            if audiosauna_filtertype == '1': filter_type = ['highpass', None]
            if audiosauna_filtertype == '2': filter_type = ["lowpass", "double"]

            inst_plugindata.filter_add(True, filter_cutoff, filter_reso, filter_type[0], filter_type[1])

            f_attack, f_decay, f_release, f_sustain = setasdr(
                float(getvalue(x_device_sound, 'filterAttack', 0)), 
                float(getvalue(x_device_sound, 'filterDecay', 0)), 
                float(getvalue(x_device_sound, 'filterRelease', 0)), 
                float(getvalue(x_device_sound, 'filterSustain', 0)))

            audiosauna_lfoActive = getvalue(x_device_sound, 'lfoActive', 'false')
            audiosauna_lfoToggled = getvalue(x_device_sound, 'lfoToggled', 'false')
            audiosauna_lfoTime = float(getvalue(x_device_sound, 'lfoTime', 1))
            audiosauna_lfoFilter = float(getvalue(x_device_sound, 'lfoFilter', 0))
            audiosauna_lfoPitch = float(getvalue(x_device_sound, 'lfoPitch', 0))
            audiosauna_lfoDelay = float(getvalue(x_device_sound, 'lfoDelay', 0))
            audiosauna_lfoWaveForm = getvalue(x_device_sound, 'lfoWaveForm', '0')

            if audiosauna_lfoWaveForm == '0': audiosauna_lfoWaveForm = "tri"
            if audiosauna_lfoWaveForm == '1': audiosauna_lfoWaveForm = 'square'
            if audiosauna_lfoWaveForm == '2': audiosauna_lfoWaveForm = "random"
            if audiosauna_lfoToggled == 'true': audiosauna_lfoToggled = 1
            if audiosauna_lfoToggled == 'false': audiosauna_lfoToggled = 0
            p_lfo_amount = ((audiosauna_lfoPitch/100)*12)*audiosauna_lfoToggled
            c_lfo_amount = ((audiosauna_lfoFilter/100)*-7200)*audiosauna_lfoToggled
            g_lfo_attack = audiosauna_lfoDelay
            g_lfo_shape = audiosauna_lfoWaveForm
            g_lfo_speed = audiosauna_lfoTime

            inst_plugindata.lfo_add('pitch', g_lfo_shape, 'seconds', g_lfo_speed, 0, g_lfo_attack, p_lfo_amount)
            inst_plugindata.lfo_add('cutoff', g_lfo_shape, 'seconds', g_lfo_speed, 0, g_lfo_attack, c_lfo_amount)
            
            tracks_r.track_inst_pluginid(cvpj_l, cvpj_trackid, pluginid)

            for fx_name in ['distortion', 'bitcrush', 'chorus', 'amp']:
                fxslot.insert(cvpj_l, ['track', cvpj_trackid], 'audio', make_fxslot(x_proj, fx_name, v_device_deviceType))

            inst_plugindata.to_cvpj(cvpj_l, pluginid)
            devicenum += 1

        as_loopstart = float(getvalue(x_proj, 'appLoopStart', 0))
        as_loopend = float(getvalue(x_proj, 'appLoopEnd', 0))
        if as_loopstart != 0 and as_loopend != 0: song.add_timemarker_looparea(cvpj_l, None, as_loopstart, as_loopend)

        song.add_param(cvpj_l, 'bpm', x_BPM)
        return json.dumps(cvpj_l)


