# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

#import math
#from dawvertplus.functions import note_mod
#from dawvertplus.functions import notelist_data
from dawvertplus.functions import song
#from dawvertplus.functions import xtramath

def getsongduration(projJ):
    trackplacements = projJ['track_placements']
    songduration = 0
    for trackid in trackplacements:

        islaned = False
        if 'laned' in trackplacements[trackid]:
            if trackplacements[trackid]['laned'] == 1:
                islaned = True

        if islaned == False:
            if 'notes' in trackplacements[trackid]:
                for placement in trackplacements[trackid]['notes']:
                    p_pos = placement['position']
                    p_dur = placement['duration']
                    if songduration < p_pos+p_dur:
                        songduration = p_pos+p_dur
        else:
            if 'lanedata' in trackplacements[trackid]:
                for s_lanedata in trackplacements[trackid]['lanedata']:
                    placementdata = trackplacements[trackid]['lanedata'][s_lanedata]['notes']
                    for placement in placementdata:
                        p_pos = placement['position']
                        p_dur = placement['duration']
                        if songduration < p_pos+p_dur:
                            songduration = p_pos+p_dur

    return songduration + 64

points_items = None


def get_timesig(patternLength, notesPerBeat):
    MaxFactor = 1024
    factor = 1
    while (((patternLength * factor) % notesPerBeat) != 0 and factor <= MaxFactor):
        factor *= 2
    foundValidFactor = ((patternLength * factor) % notesPerBeat) == 0
    numer = 4
    denom = 4

    if foundValidFactor == True:
        numer = patternLength * factor / notesPerBeat
        denom = 4 * factor
    else: 
        print('Error computing valid time signature, defaulting to 4/4.')

    return [int(numer), denom]

def make_timemarkers(cvpj_l, timesig, PatternLengthList, LoopPos):
    prevtimesig = timesig
    timemarkers = []
    currentpos = 0
    blockcount = 0
    for PatternLengthPart in PatternLengthList:
        temptimesig = get_timesig(PatternLengthPart, timesig[1])
        if prevtimesig != temptimesig:
            song.add_timemarker_timesig(cvpj_l, str(temptimesig[0])+'/'+str(temptimesig[1]), currentpos, temptimesig[0], temptimesig[1])
        if LoopPos == blockcount:
            if prevtimesig != temptimesig: timemarkerloopname = str(temptimesig[0])+'/'+str(temptimesig[1]) + " & Loop"
            else: timemarkerloopname = "Loop"
            song.add_timemarker_loop(cvpj_l, currentpos, timemarkerloopname)
        prevtimesig = temptimesig
        currentpos += PatternLengthPart
        blockcount += 1
