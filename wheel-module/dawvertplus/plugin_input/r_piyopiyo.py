# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dawvertplus.plugin_input import base
import json
import struct
#import os.path
#from dawvertplus.functions import audio_wav
#from dawvertplus.functions import data_bytes
from dawvertplus.functions import placement_data
from dawvertplus.functions import plugins
from dawvertplus.functions import song
from dawvertplus.functions import note_data
from dawvertplus.functions import colors
from dawvertplus.functions import data_dataset
from dawvertplus.functions_tracks import tracks_r

class input_piyopiyo(base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'piyopiyo'
    def getname(self): return 'PiyoPiyo'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'auto_nopl': True,
        'track_nopl': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(3)
        if bytesdata == b'PMD': return True
        else: return False
    def parse(self, input_file, extra_param):
        pmdfile = open(input_file, 'rb')
        header = pmdfile.read(4)
        trackdatapos = int.from_bytes(pmdfile.read(4), "little")
        musicwait = int.from_bytes(pmdfile.read(4), "little")
        bpm = (120/musicwait)*120
        print("[input-piyopiyo] MusicWait: " + str(musicwait))
        loopstart = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] Loop Beginning: " + str(loopstart))
        loopend = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] Loop End: " + str(loopend))
        recordspertrack = int.from_bytes(pmdfile.read(4), "little")
        print("[input-piyopiyo] Records Per Track: " + str(recordspertrack))

        pmdtrackdata = []
        keyoffset = [0,0,0,0]

        cvpj_l = {}

        dataset = data_dataset.dataset('./data_dset/piyopiyo.dset')
        colordata = colors.colorset(dataset.colorset_e_list('inst', 'main'))

        for tracknum in range(3):
            print("[input-piyopiyo] Track " + str(tracknum+1), end=",")
            trk_octave = pmdfile.read(1)[0]
            print(" Oct:" + str(trk_octave), end=",")
            trk_icon = pmdfile.read(1)[0]
            print(" Icon:" + str(trk_icon), end=",")
            trk_unk = pmdfile.read(2)
            trk_length = int.from_bytes(pmdfile.read(4), "little")
            print(" Len:" + str(trk_length), end=",")
            trk_volume = int.from_bytes(pmdfile.read(4), "little")
            print(" Vol:" + str(trk_volume))
            trk_unk2 = pmdfile.read(8)
            trk_waveform = struct.unpack('b'*256, pmdfile.read(256))
            trk_envelope = struct.unpack('B'*64, pmdfile.read(64))
            keyoffset[tracknum] = (trk_octave-2)*12
            idval = str(tracknum)

            pluginid = str(tracknum)
            inst_plugindata = plugins.cvpj_plugin('deftype', 'universal', 'synth-osc')
            inst_plugindata.osc_num_oscs(1)
            inst_plugindata.osc_opparam_set(0, 'shape', 'custom_wave')
            inst_plugindata.osc_opparam_set(0, 'wave_name', 'main')
            inst_plugindata.wave_add('main', trk_waveform, -128, 128)
            inst_plugindata.env_blocks_add('vol', trk_envelope, 1/64, 128, None, None)
            inst_plugindata.env_points_from_blocks('vol')
            inst_plugindata.to_cvpj(cvpj_l, pluginid)

            tracks_r.track_create(cvpj_l, idval, 'instrument')
            tracks_r.track_visual(cvpj_l, idval, name='Inst #'+str(tracknum), color=colordata.getcolornum(tracknum))
            tracks_r.track_inst_pluginid(cvpj_l, idval, pluginid)
            tracks_r.track_param_add(cvpj_l, idval, 'vol', trk_volume/250, 'float')

        TrackPVol = int.from_bytes(pmdfile.read(4), "little")

        inst_plugindata = plugins.cvpj_plugin('deftype', 'native-piyopiyo', 'drums')
        inst_plugindata.to_cvpj(cvpj_l, "3")

        tracks_r.track_create(cvpj_l, "3", 'instrument')
        tracks_r.track_visual(cvpj_l, "3", name='perc', color=colordata.getcolornum(3))
        tracks_r.track_inst_pluginid(cvpj_l, "3", "3")
        tracks_r.track_param_add(cvpj_l, "3", 'vol', TrackPVol/250, 'float')

        pmdfile.seek(trackdatapos)
        for tracknum in range(4):
            notelist = []
            t_placements = []
            currentpan = 0
            for pmdpos in range(recordspertrack):
                bitnotes = bin(int.from_bytes(pmdfile.read(3), "little"))[2:].zfill(24)
                pan = pmdfile.read(1)[0]
                if pan != 0: currentpan = (pan-4)/3
                notenum = 11
                for bitnote in bitnotes:
                    if bitnote == '1': notelist.append(note_data.rx_makenote(pmdpos, 1, notenum+keyoffset[tracknum], 1.0, currentpan))
                    notenum -= 1
            t_placements = placement_data.nl2pl(notelist) if notelist != [] else []
            tracks_r.add_pl(cvpj_l, str(tracknum), 'notes', t_placements)

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True
        song.add_param(cvpj_l, 'bpm', bpm)

        song.add_timemarker_looparea(cvpj_l, None, loopstart, loopend)
        return json.dumps(cvpj_l)