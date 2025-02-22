# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dawvertplus.functions import data_bytes
from dawvertplus.functions import data_values
from dawvertplus.functions import note_data
from dawvertplus.functions import placement_data
from dawvertplus.functions import plugins
from dawvertplus.functions import song
from dawvertplus.functions import colors
from dawvertplus.functions import data_dataset
from dawvertplus.functions_tracks import tracks_rm
from dawvertplus.functions_tracks import tracks_master
from dawvertplus.functions_tracks import fxslot
from dawvertplus.plugin_input import base
import base64
import json
import zlib

def tnotedata_to_cvpj_nl(cvpj_notelist, instid, in_notedata, note):
    for tnote in in_notedata:
        duration = tnote[1]['duration'] if 'duration' in tnote[1] else 1
        cvpj_notelist.append(note_data.mx_makenote(instid, tnote[0], duration, note, tnote[1]['velocity'], 0))
    return cvpj_notelist

def get_instids(instdata):
    outdata = []
    for instnum in range(len(instdata)):
        si = instdata[instnum]
        instid = str(int(si['on']))+'_'+str(si['audioClipId'])+'_'+str(si['volume'])
        used_instrument_data[instid] = si
        outdata.append(instid)
    return outdata

def decodeblock(cvpj_l, input_block, position):
    pl_dur = 128
    repeatdur = 0

    columns = input_block['columns']
    notesdata = input_block['notes']
    instdata = input_block['instruments']
    drumsdata = input_block['drums']

    for repeatnum in range(8):
        if columns[repeatnum]['repeat'] == True:
            repeatdur += 16
            pl_dur = repeatdur
        else:
            break

    blockinsts = get_instids(instdata)

    blockdrums = get_instids(drumsdata)

    t_notedata_drums = [[] for x in range(5)]
    t_notedata_inst = [[[] for x in range(16)] for x in range(4)]

    datafirst = data_values.list_chunks(notesdata, 9*128)

    for firstnum in range(len(datafirst)):
        datasecond = datafirst[firstnum]
        datathird = data_values.list_chunks(datasecond, 9)
        for thirdnum in range(128):
            stepnum = ((thirdnum&0b0000111)<<4)+((thirdnum&0b1111000)>>3)
            forthdata = datathird[thirdnum]
            for notevirt in range(9):
                notevirt_t = -notevirt+8 + firstnum*9
                if forthdata[notevirt]['velocity'] != 0.0:
                    tnotedata = [stepnum, forthdata[notevirt]]
                    if notevirt_t < 5: t_notedata_drums[notevirt_t].append(tnotedata)
                    else:
                        instnumber = notevirt_t-5
                        notenumber = instnumber//9
                        instnumber -= (instnumber//9)*9
                        t_notedata_inst[instnumber][notenumber].append(tnotedata)

    for instnum in range(4):
        instnuminv = -instnum+3
        notelist = []
        for notekey in range(16):
            notelist = tnotedata_to_cvpj_nl(notelist, blockinsts[instnum], t_notedata_inst[instnuminv][notekey], cvpj_scale[notekey])
        if notelist != []: 
            blockinstid = blockinsts[instnum]
            if blockinstid not in used_instruments:  used_instruments.append(blockinstid)
            placementdata = placement_data.makepl_n(position, pl_dur, notelist)
            placementdata['name'] = instdata[instnum]['preset']
            placementdata['color'] = colordata.getcolornum(instnum)
            longpldata = placement_data.longpl_split(placementdata)
            for longpls in longpldata:
                tracks_rm.add_pl(cvpj_l, instnum+1, 'notes', longpls)

    for drumnum in range(5):
        drumnumminv = -drumnum+4
        notelist = tnotedata_to_cvpj_nl([], blockdrums[drumnum], t_notedata_drums[drumnum], 0)
        if notelist != []: 
            blockdrumid = blockdrums[drumnum]
            if blockdrumid not in used_instruments: used_instruments.append(blockdrumid)
            placementdata = placement_data.makepl_n(position, pl_dur, notelist)
            placementdata['name'] = drumsdata[drumnum]['preset']
            placementdata['color'] = colordata.getcolornum(drumnumminv+4)
            longpldata = placement_data.longpl_split(placementdata)
            for longpls in longpldata:
                tracks_rm.add_pl(cvpj_l, drumnumminv+5, 'notes', longpls)

    return pl_dur


class input_1bitdragon(base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return '1bitdragon'
    def getname(self): return '1bitdragon'
    def gettype(self): return 'rm'
    def supported_autodetect(self): return False
    def getdawcapabilities(self): 
        return {}
    def parse(self, input_file, extra_param):
        global used_instruments
        global used_instrument_data
        global cvpj_scale
        global colordata

        song_file = open(input_file, 'r')
        basebase64stream = base64.b64decode(song_file.read())
        bio_base64stream = data_bytes.to_bytesio(basebase64stream)
        bio_base64stream.seek(4)
        decompdata = json.loads(zlib.decompress(bio_base64stream.read(), 16+zlib.MAX_WBITS))

        dataset = data_dataset.dataset('./data_dset/1bitdragon.dset')
        colordata = colors.colorset(dataset.colorset_e_list('track', 'main'))

        cvpj_l = {}
        used_instruments = []
        used_instrument_data = {}

        onebitd_bpm = decompdata['bpm']
        onebitd_reverb = decompdata['reverb']
        onebitd_scaleId = decompdata['scaleId']
        onebitd_volume = decompdata['volume']

        onebitd_scaletype = (onebitd_scaleId//12)
        onebitd_scalekey = onebitd_scaleId-(onebitd_scaletype*12)

        if onebitd_scaletype == 0: cvpj_scale = [[0 ,2 ,4 ,7 ,9 ,12,14,16,19,21,24,26,28,31,33,36] ,-24]
        if onebitd_scaletype == 1: cvpj_scale = [[0 ,3 ,5 ,7 ,10,12,15,17,19,22,24,27,29,31,34,36] ,-24]
        if onebitd_scaletype == 2: cvpj_scale = [[0 ,2 ,4 ,5 ,7 ,9 ,11,12,14,16,17,19,21,23,24,26] ,-24]
        if onebitd_scaletype == 3: cvpj_scale = [[0 ,2 ,3 ,4 ,7 ,8 ,10,12,14,15,16,19,20,22,24,26] ,-24]
        if onebitd_scaletype == 4: cvpj_scale = [[0 ,2 ,3 ,5 ,7 ,9 ,10,12,14,15,17,19,21,22,24,26] ,-24]
        if onebitd_scaletype == 5: cvpj_scale = [[0 ,1 ,4 ,5 ,6 ,9 ,10,12,13,16,17,18,21,22,24,25] ,-24]
        if onebitd_scaletype == 6: cvpj_scale = [range(16),-12]

        cvpj_scale = [x+cvpj_scale[1]+onebitd_scalekey for x in cvpj_scale[0]]

        for plnum in range(9):
            tracks_rm.track_create(cvpj_l, str(plnum+1), 'instruments')
            tracks_rm.track_visual(cvpj_l, str(plnum+1), color=colordata.getcolornum(plnum))

        curpos = 0
        for blocknum in range(len(decompdata['blocks'])):
            nextpos = decodeblock(cvpj_l, decompdata['blocks'][blocknum], curpos)
            curpos += nextpos

        for part_used_instrument in used_instruments:
            usedinstdata = used_instrument_data[part_used_instrument]
            instname = usedinstdata['preset']
            tracks_rm.inst_create(cvpj_l, part_used_instrument)
            tracks_rm.inst_visual(cvpj_l, part_used_instrument, name=instname)

            tracks_rm.inst_param_add(cvpj_l, part_used_instrument, 'vol', usedinstdata['volume'], 'float')
            tracks_rm.inst_param_add(cvpj_l, part_used_instrument, 'enabled', usedinstdata['on'], 'bool')

        song.add_param(cvpj_l, 'bpm', onebitd_bpm)

        tracks_master.create(cvpj_l, onebitd_volume)
        tracks_master.visual(cvpj_l, name='Master')

        fx_plugindata = plugins.cvpj_plugin('deftype', 'simple', 'reverb')
        fx_plugindata.fxvisual_add('Reverb', None)
        fx_plugindata.fxdata_add(onebitd_reverb, 0.5)
        fx_plugindata.to_cvpj(cvpj_l, 'master-reverb')

        fxslot.insert(cvpj_l, ['master'], 'audio', 'master-reverb')

        return json.dumps(cvpj_l)
