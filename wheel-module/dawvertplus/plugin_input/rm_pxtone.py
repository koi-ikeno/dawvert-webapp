# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

""" 
from dawvertplus.functions import data_bytes
from dawvertplus.functions import note_mod
from dawvertplus.functions import audio_wav
from dawvertplus.functions import plugins
from dawvertplus.functions import placement_data
from dawvertplus.functions import note_data
from dawvertplus.functions import song
from dawvertplus.functions import colors
from dawvertplus.functions import data_dataset
from dawvertplus.functions_tracks import tracks_rm
from dawvertplus.functions_tracks import auto_nopl
import plugin_input
import json
import math
import varint
import struct
import os

ptcop_events = {}
ptcop_events[0] = '--None--'
ptcop_events[1] = 'Note    '
ptcop_events[2] = 'Pitch   '
ptcop_events[3] = 'Pan     '
ptcop_events[4] = 'Velocity'
ptcop_events[5] = 'Volume  '
ptcop_events[6] = 'Porta   '
ptcop_events[12] = 'Voice # '
ptcop_events[13] = 'Group # '
ptcop_events[14] = 'Key Corr'
ptcop_events[15] = 'Pan Time'

def get_float(in_int): return struct.unpack("<f", struct.pack("I", in_int))[0]

def parse_event(bio_stream):
    position = varint.decode_stream(bio_stream)
    unitnum = int.from_bytes(bio_stream.read(1), "little")
    eventnum = int.from_bytes(bio_stream.read(1), "little")
    value = varint.decode_stream(bio_stream)

    if eventnum == 2: 
        pitch = (value-25344)/256
        note = int((value-25344)/256)
        value = [note, note-pitch]
    if eventnum == 4: value = value/128

    return [position, unitnum, eventnum, value]

def readextra(data):
    output = b''
    terminated = 0
    while terminated == 0:
        char = data.read(1)
        if char != b'\x00' and char != b'': output += char
        else: terminated = 1
    return output

# == unfinished
def parse_ptvoice_unit(bio_ptvoice, unitnum):
    l_unit = {}
    print('[input-ptcop]   --- Unit '+str(unitnum))

    bio_ptvoice.read(2)
    l_unit['vol'] = bio_ptvoice.read(1)[0]/64
    print('[input-ptcop]   Vol: '+str(l_unit['vol']))
    l_unit['pan'] = ((varint.decode_stream(bio_ptvoice)/128) - 0.5) *2
    print('[input-ptcop]   Pan: '+str(l_unit['pan']))
    l_unit['detune'] = ((get_float(varint.decode_stream(bio_ptvoice))-1)/0.0127)*26
    print('[input-ptcop]   Detune: '+str(l_unit['detune']))

    bio_ptvoice.read(2)

    env_wave_type = bio_ptvoice.read(1)
    if env_wave_type == b'\x00': # ------------------------------ points
        l_unit['wave_type'] = 'points'
        l_unit['wave_points'] = []
        env_wave_points = bio_ptvoice.read(1)[0]
        bio_ptvoice.read(2)
        for _ in range(env_wave_points):
            point_loc = bio_ptvoice.read(1)[0]
            point_val = int.from_bytes(bio_ptvoice.read(1), "little", signed=True)
            l_unit['wave_points'].append([point_loc, point_val/128])
        print('[input-ptcop]   Wave Points: '+str(l_unit['wave_points']))

    if env_wave_type == b'\x01': # ------------------------------ harm
        env_wave_harm = bio_ptvoice.read(1)[0]
        l_unit['wave_type'] = 'harm'
        l_unit['wave_harm'] = [0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0]
        for _ in range(env_wave_harm):
            harm_num = bio_ptvoice.read(1)[0]
            point_val = struct.unpack("i", struct.pack("I", varint.decode_stream(bio_ptvoice)))[0]/128
            l_unit['wave_harm'][harm_num-1] = point_val
        print('[input-ptcop]   Wave Harm: '+str(l_unit['wave_harm']))

    bio_ptvoice.read(2)

    l_unit['vol_points'] = []

    firstvolpoint = bio_ptvoice.read(1)
    env_vol_points = firstvolpoint[0]+1
    for _ in range(env_vol_points):
        point_loc = varint.decode_stream(bio_ptvoice)
        point_val = varint.decode_stream(bio_ptvoice)
        l_unit['vol_points'].append([point_loc, point_val])

    print('[input-ptcop]   Vol Points: '+str(len(l_unit['vol_points'])))

    l_unit['release'] = varint.decode_stream(bio_ptvoice)

    print('[input-ptcop]   Release: '+str(l_unit['release']))

    readextra(bio_ptvoice)
    
    return l_unit



def parse_matePTV(bio_stream):
    size, voice_number, tuning, sz = struct.unpack("hhfi", bio_stream.read(12))
    ptvoice_data = bio_stream.read(sz)
    l_ptvoice = {'units': []}
    bio_ptvoice = data_bytes.to_bytesio(ptvoice_data)
    ptvoice_header = bio_ptvoice.read(8)
    ptvoice_unk = int.from_bytes(bio_ptvoice.read(4), "little")
    ptvoice_size = int.from_bytes(bio_ptvoice.read(4), "little")
    ptvoice_d_num_units = int.from_bytes(bio_ptvoice.read(4), "big")
    for unitnum in range(ptvoice_d_num_units): l_ptvoice['units'].append(parse_ptvoice_unit(bio_ptvoice, unitnum))
    return l_ptvoice

def parse_assiWOIC(bio_stream, chunksize):
    voice_number = int.from_bytes(bio_stream.read(4), "little")
    print('[input-ptcop]   Voice #: '+str(voice_number))
    voice_name_bytes = bio_stream.read(chunksize-4)
    voice_name = voice_name_bytes.split(b'\x00')[0].decode("shift-jis")
    print('[input-ptcop]   Voice Name: '+str(voice_name))
    return voice_number, voice_name

def parse_assiUNIT(bio_stream, chunksize):
    unit_number = int.from_bytes(bio_stream.read(4), "little")
    print('[input-ptcop]   Unit #: '+str(unit_number))
    unit_name_bytes = bio_stream.read(chunksize-4)
    unit_name = unit_name_bytes.split(b'\x00')[0].decode("shift-jis")
    print('[input-ptcop]   Unit Name: '+str(unit_name))
    return unit_number, unit_name

class input_pxtone(base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'ptcop'
    def getname(self): return 'PxTone'
    def gettype(self): return 'rm'
    def getdawcapabilities(self): 
        return {
        'samples_inside': True,
        'track_lanes': True,
        'auto_nopl': True,
        'track_nopl': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(16)
        if bytesdata == b'PTCOLLAGE-071119': return True
        elif bytesdata == b'PTTUNE--20071119': return True
        else: return False
    def parse(self, input_file, extra_param):
        song_file = open(input_file, 'rb')
        song_file.seek(0,2)
        song_filesize = song_file.tell()
        song_file.seek(0)
        
        dataset = data_dataset.dataset('./data_dset/pxtone.dset')
        colordata = colors.colorset(dataset.colorset_e_list('track', 'main'))

        ptcop_header = song_file.read(16)
        ptcop_unk = int.from_bytes(song_file.read(4), "little")
        ptcop_unit_events = {}
        ptcop_name_voice = {}
        ptcop_name_unit = {}
        ptcop_song_name = None
        ptcop_song_comment = None
        ptcop_voice_num = 0

        if ptcop_header == b'PTCOLLAGE-071119': timebase = 120
        if ptcop_header == b'PTTUNE--20071119': timebase = 12

        t_voice_data = []

        samplefolder = extra_param['samplefolder']

        cvpj_l = {}

        while song_filesize > song_file.tell():
            chunkname = song_file.read(8)
            chunksize = int.from_bytes(song_file.read(4), "little")

            if chunkname == b'MasterV5':
                print('[input-ptcop] Chunk: Master', chunksize)
                ptcop_mas_unk1 = int.from_bytes(song_file.read(2), "little")
                ptcop_mas_beat = int.from_bytes(song_file.read(1), "little")
                print('[input-ptcop]   Beat: '+str(ptcop_mas_beat))
                ptcop_mas_unk2 = int.from_bytes(song_file.read(2), "little")
                ptcop_mas_beattempo = struct.unpack(">f", struct.pack("I", int.from_bytes(song_file.read(2), "big")))[0]
                print('[input-ptcop]   Tempo: '+str(ptcop_mas_beattempo))
                ptcop_mas_repeat = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   Repeat: '+str(ptcop_mas_repeat))
                ptcop_mas_last = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   Last: '+str(ptcop_mas_last))

            elif chunkname == b'Event V5':
                print('[input-ptcop] Chunk: Event', chunksize)
                num_of_events = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   # of events: '+str(num_of_events))
                
                cur_voice = 0
                cur_group = 0
                position_global = 0
                
                for _ in range(num_of_events):
                    eventdata = parse_event(song_file)
                    if eventdata[2] == 12: cur_voice = eventdata[3]
                    if eventdata[2] == 13: cur_group = eventdata[3]
                    if eventdata[1] not in ptcop_unit_events: ptcop_unit_events[eventdata[1]] = []
                    position_global += eventdata[0]
                    eventdata[0] = position_global
                    ptcop_unit_events[eventdata[1]].append(eventdata)
        
            elif chunkname == b'mateOGGV':
                print('[input-ptcop] Chunk: mateOGGV', chunksize)
                song_file.read(3)
                ptcop_ogg_basic_key_field = song_file.read(1)[0]
                print('[input-ptcop]   Basic Key field: '+str(ptcop_ogg_basic_key_field))
                ptcop_ogg_sps2 = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   Voice flags: '+str(ptcop_ogg_sps2))
                ptcop_ogg_loop = bool(ptcop_ogg_sps2 & 0b000000000000001)
                print('[input-ptcop]   Loop: '+str(ptcop_ogg_loop))
                ptcop_ogg_smooth = bool(ptcop_ogg_sps2 & 0b000000000000010)
                print('[input-ptcop]   Smooth: '+str(ptcop_ogg_smooth))
                ptcop_ogg_key_correct = struct.unpack("f", song_file.read(4))[0]
                print('[input-ptcop]   Key Correct: '+str(ptcop_ogg_key_correct))
                ptcop_ogg_samples = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   Channels: '+str(ptcop_ogg_samples))
                ptcop_ogg_hz = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   Hz: '+str(ptcop_ogg_hz))
                song_file.read(4)
                ptcop_ogg_datasize = int.from_bytes(song_file.read(4), "little")

                os.makedirs(samplefolder, exist_ok=True)
                ogg_path = samplefolder + 'ptcop_' + str(ptcop_voice_num+1).zfill(2) + '.ogg'
                ogg_fileobj = open(ogg_path, 'wb')
                ogg_fileobj.write(song_file.read(ptcop_ogg_datasize))
                plugindata = {'file': ogg_path, 'trigger': 'normal'}
                plugindata['interpolation'] = "linear" if ptcop_ogg_smooth else "none"
                t_voice_data.append(['sampler', plugindata, ptcop_ogg_basic_key_field-60])
                ptcop_voice_num += 1

            elif chunkname == b'matePTV ':
                print('[input-ptcop] Chunk: PTVoice', chunksize)
                song_file.read(chunksize)
                t_voice_data.append(['none', {}, 0])
                ptcop_voice_num += 1

            elif chunkname == b'matePTN ':
                print('[input-ptcop] Chunk: PTNoise', chunksize)
                song_file.read(chunksize)
                t_voice_data.append(['none', {}, 0])
                ptcop_voice_num += 1

            elif chunkname == b'matePCM ':
                print('[input-ptcop] Chunk: PCM', chunksize)
                song_file.read(3)
                ptcop_pcm_basic_key_field = song_file.read(1)[0]
                print('[input-ptcop]   Basic Key field: '+str(ptcop_pcm_basic_key_field))
                ptcop_pcm_flags = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   Voice flags: '+str(ptcop_pcm_flags))
                ptcop_pcm_loop = bool(ptcop_pcm_flags & 0b000000000000001)
                print('[input-ptcop]   Loop: '+str(ptcop_pcm_loop))
                ptcop_pcm_smooth = bool(ptcop_pcm_flags & 0b000000000000010)
                print('[input-ptcop]   Smooth: '+str(ptcop_pcm_smooth))
                ptcop_pcm_ch = int.from_bytes(song_file.read(2), "little")
                print('[input-ptcop]   Channels: '+str(ptcop_pcm_ch))
                ptcop_pcm_bits = int.from_bytes(song_file.read(2), "little")
                print('[input-ptcop]   Bits: '+str(ptcop_pcm_bits))
                ptcop_pcm_hz = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   Hz: '+str(ptcop_pcm_hz))
                ptcop_pcm_key_correct = struct.unpack("f", song_file.read(4))[0]
                print('[input-ptcop]   Key Correct: '+str(ptcop_pcm_key_correct))
                ptcop_pcm_samples = int.from_bytes(song_file.read(4), "little")//(ptcop_pcm_bits//8)
                print('[input-ptcop]   Samples: '+str(ptcop_pcm_samples)) 
                ptcop_pcm_data = song_file.read((ptcop_pcm_bits//8) * ptcop_pcm_samples)

                os.makedirs(samplefolder, exist_ok=True)
                wave_path = samplefolder + 'ptcop_' + str(ptcop_voice_num+1).zfill(2) + '.wav'

                plugindata = {'file': wave_path, 'start': 0, 'end': ptcop_pcm_samples, 'trigger': 'normal'}

                if ptcop_pcm_smooth == True: plugindata['interpolation'] = "linear"
                else: plugindata['interpolation'] = "none"

                if ptcop_pcm_loop == 1: 
                    loopdata = {'loop':[0, ptcop_pcm_samples]}
                    plugindata['loop'] = {'enabled':1, 'mode':"normal", 'points':[0, ptcop_pcm_samples]}
                else: 
                    loopdata = None
                    plugindata['loop'] = {'enabled':0, 'mode':"normal", 'points':[0, ptcop_pcm_samples]}

                audio_wav.generate(wave_path, ptcop_pcm_data, ptcop_pcm_ch, ptcop_pcm_hz, ptcop_pcm_bits, loopdata)

                t_voice_data.append(['sampler', plugindata, ptcop_pcm_basic_key_field-60])
                ptcop_voice_num += 1


            elif chunkname == b'assiWOIC':
                print('[input-ptcop] Chunk: assiWOIC', chunksize)
                assiWOIC_data = parse_assiWOIC(song_file, chunksize)
                ptcop_name_voice[assiWOIC_data[0]] = assiWOIC_data[1]

            elif chunkname == b'num UNIT':
                print('[input-ptcop] Chunk: num UNIT', chunksize)
                num_units = int.from_bytes(song_file.read(4), "little")
                print('[input-ptcop]   # of units: '+str(num_units))

            elif chunkname == b'assiUNIT':
                print('[input-ptcop] Chunk: assiUNIT', chunksize)
                assiUNIT_data = parse_assiUNIT(song_file, chunksize)
                ptcop_name_unit[assiUNIT_data[0]] = assiUNIT_data[1]

            elif chunkname == b'textNAME':
                print('[input-ptcop] Chunk: textNAME', chunksize)
                ptcop_song_name = song_file.read(chunksize).decode("shift-jis")

            elif chunkname == b'textCOMM':
                print('[input-ptcop] Chunk: textCOMM', chunksize)
                ptcop_song_comment = song_file.read(chunksize).decode("shift-jis")

            elif chunkname == b'effeDELA':
                print('[input-ptcop] Chunk: effeDELA', chunksize)
                song_file.read(chunksize)

            elif chunkname == b'effeOVER':
                print('[input-ptcop] Chunk: effeOVER', chunksize)
                song_file.read(chunksize)

            elif chunkname == b'pxtoneND':
                print('[input-ptcop] End.')
                break

            else:
                print('[input-ptcop] Unknown Chunk:', chunkname)
                exit()
            print('[input-ptcop]')

        t_notelist = {}

        velpanpos = None
        unitnum = 0

        trackautop = []

        for unit_eventnum in ptcop_unit_events:
            cvpj_trackid = str(unitnum+1)
            t_notelist[unit_eventnum] = []
            prevpos = 0
            position_global = 0
            noteend = 0
            notedur = 0
            cur_pitch = 9
            cur_porta = 0
            cur_voice = 0

            auto_vol = {}
            auto_pan = {}
            auto_pitch = {}

            firstnote = None

            for unit_event in ptcop_unit_events[unit_eventnum]:
                #print(
                #    str(unit_event[0]).ljust(6),
                #    str(unit_event[1]).ljust(2),
                #    str(unit_event[2]).ljust(2),
                #    ptcop_events[unit_event[2]],
                #    str(unit_event[3]).ljust(12),
                #    str(noteend).ljust(7),
                #    )

                if unit_event[2] == 2: cur_pitch = unit_event[3][0]+12
                if unit_event[2] == 6: cur_porta = unit_event[3]/timebase
                if unit_event[2] == 12: cur_voice = unit_event[3]
                position_global = unit_event[0]

                if unit_event[2] == 1: 
                    if firstnote == None: firstnote = velpanpos
                    velpanpos = unit_event[0]
                    notedur = unit_event[3]
                    noteend = position_global+notedur
                    noteon_note = cur_pitch
                    cvpj_note = note_data.mx_makenote('ptcop_'+str(cur_voice), position_global/timebase, notedur/timebase, noteon_note, None, None)
                    t_notelist[unit_eventnum].append(cvpj_note)

                prevpos = unit_event[0]
                
                if t_notelist[unit_eventnum] != []:
                    lastnotedata = t_notelist[unit_eventnum][-1]
                    if 'notemod' not in lastnotedata: lastnotedata['notemod'] = {'slide': [], 'auto': {}}

                if unit_event[2] == 5: auto_vol[unit_event[0]] = unit_event[3]/128
                if unit_event[2] == 15: auto_pan[unit_event[0]] = ((unit_event[3]/128)-0.5)*2
                if unit_event[2] == 14: auto_pitch[unit_event[0]] = math.log2(get_float(unit_event[3]))*12
                if unit_event[2] == 2 and (0 <= (unit_event[0]-noteend)+notedur < notedur): lastnotedata['notemod']['slide'].append({'position': ((unit_event[0]-noteend)+notedur)/timebase, 'duration': cur_porta, 'key': cur_pitch-noteon_note})

                if velpanpos == unit_event[0]:
                    if unit_event[2] == 3: t_notelist[unit_eventnum][-1]['pan'] = ((unit_event[3]/128)-0.5)*2
                    if unit_event[2] == 4: t_notelist[unit_eventnum][-1]['vol'] = unit_event[3]

            out_vol = auto_nopl.paramauto(['track', cvpj_trackid, 'vol'], 'float', auto_vol, timebase, firstnote, 1, 1, 0)
            out_pan = auto_nopl.paramauto(['track', cvpj_trackid, 'pan'], 'float', auto_pan, timebase, firstnote, 0, 1, 0)
            out_pitch = auto_nopl.paramauto(['track', cvpj_trackid, 'pitch'], 'float', auto_pitch, timebase, firstnote, 0, 1, 0)

            trackautop.append([out_vol,out_pan,out_pitch])

            unitnum += 1

        for unitnum in t_notelist:
            cvpj_notelist = t_notelist[unitnum]
            cvpj_trackparams = trackautop[unitnum]
            for cvpj_note in cvpj_notelist: note_mod.notemod_conv(cvpj_note)
            plt_name = ptcop_name_unit[unitnum] if unitnum in ptcop_name_unit else None
            cvpj_instcolor = colordata.getcolor()
            cvpj_trackid = str(unitnum+1)
            tracks_rm.track_create(cvpj_l, cvpj_trackid, 'instruments')
            tracks_rm.track_visual(cvpj_l, cvpj_trackid, name=plt_name, color=cvpj_instcolor)
            tracks_rm.add_pl(cvpj_l, cvpj_trackid, 'notes', placement_data.nl2pl(cvpj_notelist))

            tracks_rm.track_param_add(cvpj_l, cvpj_trackid, 'vol', cvpj_trackparams[0], 'float')
            tracks_rm.track_param_add(cvpj_l, cvpj_trackid, 'pan', cvpj_trackparams[1], 'float')
            tracks_rm.track_param_add(cvpj_l, cvpj_trackid, 'pitch', cvpj_trackparams[2], 'float')

        for voicenum in range(ptcop_voice_num):
            cvpj_instname = ptcop_name_voice[voicenum] if voicenum in ptcop_name_voice else ''
            cvpj_instvol = 0.3 if t_voice_data[voicenum][0] == 'sampler' else 1.0
            pluginid = plugins.get_id()

            cvpj_instid = 'ptcop_'+str(voicenum)

            tracks_rm.inst_create(cvpj_l, cvpj_instid)
            tracks_rm.inst_visual(cvpj_l, cvpj_instid, name=cvpj_instname, color=[0.14, 0.00, 0.29])

            plugindata = t_voice_data[voicenum][1]
            if t_voice_data[voicenum][0] == 'sampler':

                inst_plugindata = plugins.cvpj_plugin('sampler', plugindata['file'], None)
                inst_plugindata.dataval_add('trigger', plugindata['trigger'])
                inst_plugindata.dataval_add('interpolation', plugindata['interpolation'])
                inst_plugindata.asdr_env_add('vol', 0, 0, 0, 0, 1, 0, 1)
                inst_plugindata.to_cvpj(cvpj_l, pluginid)

                tracks_rm.inst_pluginid(cvpj_l, cvpj_instid, pluginid)

            tracks_rm.inst_param_add(cvpj_l, cvpj_instid, 'vol', cvpj_instvol, 'float')
            tracks_rm.inst_dataval_add(cvpj_l, cvpj_instid, 'instdata', 'middlenote', t_voice_data[voicenum][2])

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True
        
        song.add_timesig(cvpj_l, ptcop_mas_beat, 4)

        if ptcop_song_name != None: song.add_info(cvpj_l, 'title', ptcop_song_name)
        if ptcop_song_comment != None: song.add_info_msg(cvpj_l, 'text', ptcop_song_comment)
        if ptcop_mas_repeat != 0: song.add_timemarker_looparea(cvpj_l, None, ptcop_mas_repeat/timebase, ptcop_mas_last/timebase)

        auto_nopl.to_cvpj(cvpj_l)

        song.add_param(cvpj_l, 'bpm', ptcop_mas_beattempo)
        return json.dumps(cvpj_l)

"""