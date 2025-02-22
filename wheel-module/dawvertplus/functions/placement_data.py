# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dawvertplus.functions import notelist_data
from dawvertplus.functions import data_values
import math
#import pprint

def makepl_n(t_pos, t_dur, t_notelist):
    pl_data = {}
    pl_data['position'] = t_pos
    pl_data['duration'] = t_dur
    pl_data['notelist'] = t_notelist
    return pl_data

def makepl_n_mi(t_pos, t_dur, t_fromindex):
    pl_data = {}
    pl_data['position'] = t_pos
    pl_data['duration'] = t_dur
    pl_data['fromindex'] = t_fromindex
    return pl_data

def nl2pl(cvpj_notelist):
    return [{'position': 0, 'duration': notelist_data.getduration(cvpj_notelist), 'notelist': cvpj_notelist}]

def findsame(blocksdata, splitnum):
    if splitnum == 1: return data_values.ifallsame(blocksdata)
    else: 
        splitdata = data_values.list_chunks(blocksdata, splitnum)
        return data_values.ifallsame(splitdata)

def longpl_blkmerge(plblocks, steps):
    notelist = []
    for blocknum in range(len(plblocks)):
        partnotelist = plblocks[blocknum][1]
        for partnotelist_s in partnotelist:
            partnotelist_s['position'] += blocknum*steps
        notelist += partnotelist
    return notelist

validdursplit = [64, 128, 256]

def longpl_split(placement_data):
    plpos = placement_data['position']
    pldur = placement_data['duration']
    notelist = data_values.sort_pos(placement_data['notelist'])
    outpl = [placement_data]

    if (pldur % 16 == 0):
        split_notelists = [[0,[]] for x in range(pldur//16)]
        len_split_notelists = len(split_notelists)
        len_split_notelists_half = len_split_notelists//2

        for note in notelist:
            notepos = note['position']
            notedur = note['duration']
            blocknum = notepos//16
            blocknotepos = notepos%16
            blocksoverflow = math.ceil((blocknotepos+max(notedur,1)-1)//16)
            overflowrange = range(blocknum, blocknum+blocksoverflow)
            for ofnum in overflowrange:
                overflownum = ofnum-blocknum+1
                if split_notelists[ofnum][0] < overflownum:
                    split_notelists[ofnum][0] = overflownum
            #print(notepos, '|', blocknum, blocknotepos, '|', notedur, '|', overflowrange)
            notecpy = note.copy()
            notecpy['position'] = blocknotepos
            if blocknum < len_split_notelists:
                split_notelists[blocknum][1].append(notecpy)

        #for test in split_notelists:
        #    print(str(test[0]).rjust(3), str(len(test[1])).ljust(3), '|', end=' ')
        #print()

        basepl = placement_data.copy()
        pl_color = data_values.get_value(basepl, 'color', None)
        pl_name = data_values.get_value(basepl, 'name', None)

        # ---------------------------- repeating notes ----------------------------
        repeatingnotesfound = False
        if pldur in validdursplit:
            cursamesplit = 1
            while cursamesplit != pldur//16:
                repeatingnotesfound = findsame(split_notelists, cursamesplit)
                if repeatingnotesfound == True: break
                cursamesplit *= 2

            if repeatingnotesfound == True:
                repeatingnotelist = longpl_blkmerge(split_notelists[0:cursamesplit], 16)
                outpl = []
                for repeatnum in range((pldur//16)//cursamesplit):
                    repeatpldata = makepl_n(plpos+((repeatnum*cursamesplit)*16), cursamesplit*16, repeatingnotelist)
                    if pl_color != None: repeatpldata['color'] = pl_color
                    if pl_name != None: repeatpldata['name'] = pl_name
                    outpl.append(repeatpldata)

        # ---------------------------- autosplit ----------------------------
        if repeatingnotesfound == False:
            splitareas = []
            for split_notelist in split_notelists:
                splitareas.append(bool(split_notelist[0]) or bool(len(split_notelist[1])))
            if all(splitareas) == False:
                curblocknum = 0
                outpl = []
                for splitarea in data_values.list_findrepeat(splitareas):
                    if splitarea[0] == True:
                        splitnotelist = longpl_blkmerge(split_notelists[curblocknum:curblocknum+splitarea[1]], 16)
                        splitpldata = makepl_n(
                            plpos+(curblocknum*16), 
                            ((curblocknum+splitarea[1])-curblocknum)*16, 
                            splitnotelist)
                        if pl_color != None: splitpldata['color'] = pl_color
                        if pl_name != None: splitpldata['name'] = pl_name
                        outpl.append(splitpldata)
                    curblocknum += splitarea[1]
            elif pldur in validdursplit[1:]:

                # ---------------------------- half notes ----------------------------
                ifhalfsplitpossable = split_notelists[(len_split_notelists//2)-1][0]
                if ifhalfsplitpossable == 0:
                    first_nl = longpl_blkmerge(split_notelists[0:len_split_notelists_half], 16)
                    second_nl = longpl_blkmerge(split_notelists[len_split_notelists_half:len_split_notelists], 16)
                    halfnotelist = [first_nl, second_nl]

                    outpl = []
                    for halfsplitnum in range(2):
                        splitpldata = makepl_n(
                            plpos+(halfsplitnum*16*len_split_notelists_half), 
                            (16*len_split_notelists_half), 
                            halfnotelist[halfsplitnum])
                        if pl_color != None: splitpldata['color'] = pl_color
                        if pl_name != None: splitpldata['name'] = pl_name
                        outpl += longpl_split(splitpldata)



    return outpl

def unminus(cvpj_pl):
    if 'cut' in cvpj_pl:
        cvpj_pl_cut = cvpj_pl['cut']

        offset = 0
        if cvpj_pl_cut['type'] in ['loop_adv', 'cut']:
            if cvpj_pl_cut['start'] < 0: 
                offset = math.ceil(-cvpj_pl_cut['start']/16)*16

            if offset != 0:
                if 'loopstart' in cvpj_pl_cut: cvpj_pl_cut['loopstart'] += offset
                if 'loopend' in cvpj_pl_cut: cvpj_pl_cut['loopend'] += offset
                if 'start' in cvpj_pl_cut: cvpj_pl_cut['start'] += offset

    if offset != 0:
        if 'notelist' in cvpj_pl: cvpj_pl['notelist'] = notelist_data.move(cvpj_pl['notelist'], offset)

def cutloopdata(start, loopstart, loopend):
    out = {}
    if start == 0 and loopstart == 0:
        out['type'] = 'loop'
        out['loopend'] = loopend
    elif loopstart == 0:
        out['type'] = 'loop_off'
        out['start'] = start
        out['loopend'] = loopend
    else:
        out['type'] = 'loop_adv'
        out['start'] = start
        out['loopstart'] = loopstart
        out['loopend'] = loopend
    return out

def audiotrim(pls_data, basepos, startat, endat):
    #print('audiotrim')
    out_plsdata = []
    for pl_data in pls_data:
        plpos = pl_data['position']
        pldur = pl_data['duration']
        plcut = pl_data['cut'] if 'cut' in pl_data else None
        plend = plpos+pldur
        orgoffset = 0
        if plcut != None: orgoffset = plcut['start']

        start2, end2 = startat, plend
        start1, end1 = plpos, endat

        overlap_left = max((start2-start1), 0)
        overlap_right = max((end2-end1), 0)

        out_plpos, out_pldur = pl_data['position'], pl_data['duration']

        idoutpl = False
        if overlap_left == 0 and overlap_right == 0:
            idoutpl = True

        if overlap_left != 0 and overlap_right == 0: 
            ol_plpos = overlap_left
            if pldur > ol_plpos: 
            #    print(' ==|==  |  ', end=' - ')
                out_plpos += ol_plpos
                out_pldur -= overlap_left
            #    print(pl_data['position'], pldur)
                pl_data['cut'] = {'type': 'cut', 'start':overlap_left+orgoffset}
                idoutpl = True
            #else:
            #    print('===|    |  ')

        if overlap_left == 0 and overlap_right != 0: 
            #print('   |  ==|== - ', end='')
            #print(out_plpos, out_pldur, overlap_left, overlap_right)
            out_pldur -= overlap_right
            if out_pldur > 0: 
                pl_data['cut'] = {'type': 'cut', 'start':0+orgoffset}
                idoutpl = True

        if overlap_left != 0 and overlap_right != 0: 
            #print(' ==|====|== - ', end='')
            out_plpos += overlap_left
            out_pldur -= overlap_right+overlap_left
            #print(out_plpos, out_plpos+overlap_left, plend-plpos)
            if out_pldur > 0 and plend-plpos > out_plpos+overlap_left: 
                pl_data['cut'] = {'type': 'cut', 'start':out_plpos-plpos+orgoffset}
                idoutpl = True

        if idoutpl != False:
            out_pl = pl_data.copy()
            out_pl['position'] = out_plpos+basepos
            out_pl['duration'] = out_pldur
            out_plsdata.append(out_pl)

    return out_plsdata
