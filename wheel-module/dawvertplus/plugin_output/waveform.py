# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dawvertplus.plugin_output import base
import json
import lxml.etree as ET
from dawvertplus.functions import colors
#from dawvertplus.functions import data_values
#from dawvertplus.functions import note_data
from dawvertplus.functions import params
from dawvertplus.functions import plugins
from dawvertplus.functions import xtramath
from dawvertplus.functions import song
from dawvertplus.functions import data_dataset
from dawvertplus.functions_tracks import tracks_r
#import math

def get_plugins(xml_tag, cvpj_fxids):
    for cvpj_fxid in cvpj_fxids:
        fx_plugindata = plugins.cvpj_plugin('cvpj', cvpj_l, cvpj_fxid)
        plugtype = fx_plugindata.type_get()
        fx_on, fx_wet = fx_plugindata.fxdata_get()

        if plugtype[0] == 'native-tracktion':
            wf_PLUGIN = ET.SubElement(xml_tag, "PLUGIN")
            wf_PLUGIN.set('type', plugtype[1])
            wf_PLUGIN.set('presetDirty', '1')
            wf_PLUGIN.set('enabled', str(fx_on))

            paramlist = dataset.params_list('plugin', plugtype[1])

            for paramid in paramlist:
                dset_paramdata = dataset.params_i_get('plugin', plugtype[1], paramid)
                paramdata = fx_plugindata.param_get(paramid, dset_paramdata[2])[0]
                wf_PLUGIN.set(paramid, str(paramdata))



class output_waveform_edit(base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'Waveform Edit'
    def getshortname(self): return 'waveform_edit'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': ['loop', 'loop_off', 'loop_adv'],
        'time_seconds': True,
        'track_hybrid': True,
        'placement_audio_stretch': ['rate']
        }
    def getsupportedplugformats(self): return []
    def getsupportedplugins(self): return ['universal:compressor', 'universal:expander']
    def getfileextension(self): return 'tracktionedit'
    def parse(self, convproj_json, output_file):
        global cvpj_l
        global dataset

        wf_proj = ET.Element("EDIT")
        wf_proj.set('appVersion', "Waveform 11.5.18")
        wf_proj.set('modifiedBy', "DawVert")

        cvpj_l = json.loads(convproj_json)

        dataset = data_dataset.dataset('./data_dset/waveform.dset')

        wf_bpmdata = 120
        wf_numerator = 4
        wf_denominator = 4
        wf_bpmdata = params.get(cvpj_l, [], 'bpm', 120)[0]
        wf_numerator, wf_denominator = song.get_timesig(cvpj_l)

        tempomul = 120/wf_bpmdata

        wf_globalid = 1000

        wf_TEMPOSEQUENCE = ET.SubElement(wf_proj, "TEMPOSEQUENCE")
        wf_TEMPO = ET.SubElement(wf_TEMPOSEQUENCE, "TEMPO")
        wf_TEMPO.set('startBeat', str(0.0))
        wf_TEMPO.set('bpm', str(wf_bpmdata))
        wf_TEMPO.set('curve', str(1.0))
        wf_TIMESIG = ET.SubElement(wf_TEMPOSEQUENCE, "TIMESIG")
        wf_TIMESIG.set('numerator', str(wf_numerator))
        wf_TIMESIG.set('denominator', str(wf_denominator))
        wf_TIMESIG.set('startBeat', str(0.0))

        if 'track_master' in cvpj_l:
            cvpj_track_master = cvpj_l['track_master']

            wf_MASTERPLUGINS = ET.SubElement(wf_proj, "MASTERPLUGINS")
            if 'chain_fx_audio' in cvpj_track_master: 
                get_plugins(wf_MASTERPLUGINS, cvpj_track_master['chain_fx_audio'])

            wf_MASTERTRACK = ET.SubElement(wf_proj, "MASTERTRACK")
            wf_MASTERTRACK.set('id', str(wf_globalid))
            if 'name' in cvpj_track_master: wf_MASTERTRACK.set('name', cvpj_track_master['name'])
            wf_globalid =+ 1

        for cvpj_trackid, s_trackdata, track_placements in tracks_r.iter(cvpj_l):

            wf_TRACK = ET.SubElement(wf_proj, "TRACK")
            wf_TRACK.set('id', str(wf_globalid))
            if 'name' in s_trackdata: wf_TRACK.set('name', s_trackdata['name'])
            if 'color' in s_trackdata: wf_TRACK.set('colour', 'ff'+colors.rgb_float_to_hex(s_trackdata['color']))
            
            #cvpj_track_vol = params.get(s_trackdata, [], 'vol', 1.0)
            #cvpj_track_pan = params.get(s_trackdata, [], 'pan', 0)

            #wf_PLUGINVOLPAN = ET.SubElement(wf_TRACK, "PLUGIN")
            #wf_PLUGINVOLPAN.set('type', 'volume')
            #wf_PLUGINVOLPAN.set('enabled', '1')
            #wf_PLUGINVOLPAN.set('volume', str(cvpj_track_vol))
            #wf_PLUGINVOLPAN.set('pan', str(cvpj_track_pan))

            wf_INST = ET.SubElement(wf_TRACK, "PLUGIN")
            wf_INST.set('type', '4osc')
            wf_INST.set('enabled', '1')

            if 'chain_fx_audio' in s_trackdata: 
                get_plugins(wf_TRACK, s_trackdata['chain_fx_audio'])

            wf_PLUGINMETER = ET.SubElement(wf_TRACK, "PLUGIN")
            wf_PLUGINMETER.set('type', 'level')
            wf_PLUGINMETER.set('enabled', '1')

            if 'notes' in track_placements:
                cvpj_midiplacements = track_placements['notes']
                for cvpj_midiplacement in cvpj_midiplacements:

                    wf_MIDICLIP = ET.SubElement(wf_TRACK, "MIDICLIP")
                    if 'cut' in cvpj_midiplacement:
                        cutdata = cvpj_midiplacement['cut']
                        if cutdata['type'] == 'cut':
                            wf_MIDICLIP.set('offset', str((cutdata['start']/8)*tempomul))
                            wf_MIDICLIP.set('start', str(cvpj_midiplacement['position']))
                            wf_MIDICLIP.set('length', str(cvpj_midiplacement['duration']))
                        if cutdata['type'] in ['loop', 'loop_off', 'loop_adv']:
                            wf_MIDICLIP.set('start', str(cvpj_midiplacement['position']))
                            wf_MIDICLIP.set('length', str(cvpj_midiplacement['duration']))
                            wf_MIDICLIP.set('offset', str((cutdata['start']/8 if 'start' in cutdata else 0)*tempomul))
                            wf_MIDICLIP.set('loopStartBeats', str((cutdata['loopstart']/4 if 'loopstart' in cutdata else 0)))
                            wf_MIDICLIP.set('loopLengthBeats', str((cutdata['loopend']/4)))
                    else:
                        wf_MIDICLIP.set('start', str(cvpj_midiplacement['position']))
                        wf_MIDICLIP.set('length', str(cvpj_midiplacement['duration']))

                    if 'name' in cvpj_midiplacement: wf_MIDICLIP.set('name', cvpj_midiplacement['name'])
                    if 'color' in cvpj_midiplacement: wf_MIDICLIP.set('colour', 'ff'+colors.rgb_float_to_hex(cvpj_midiplacement['color']))
                    if 'muted' in cvpj_midiplacement: wf_MIDICLIP.set('mute', str(int(cvpj_midiplacement['muted'])))
                    if 'notelist' in cvpj_midiplacement: 
                        wf_SEQUENCE = ET.SubElement(wf_MIDICLIP, "SEQUENCE")
                        wf_SEQUENCE.set('ver', '1')
                        wf_SEQUENCE.set('channelNumber', '1')
                        for cvpj_note in cvpj_midiplacement['notelist']:
                            wf_NOTE = ET.SubElement(wf_SEQUENCE, "NOTE")
                            wf_NOTE.set('p', str(cvpj_note['key']+60))
                            wf_NOTE.set('b', str(cvpj_note['position']/4))
                            wf_NOTE.set('l', str(cvpj_note['duration']/4))
                            note_volume = cvpj_note['vol'] if 'vol' in cvpj_note else 1
                            wf_NOTE.set('v', str(int(xtramath.clamp(note_volume*127, 0, 127))))

            wf_globalid += 1

        outfile = ET.ElementTree(wf_proj)
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8', xml_declaration = True)
