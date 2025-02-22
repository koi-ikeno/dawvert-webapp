# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dawvertplus.plugin_input import base
import json
from dawvertplus.functions import placement_data
from dawvertplus.functions import note_data
from dawvertplus.functions import song
from dawvertplus.functions_tracks import tracks_r

class input_fmf(base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'flipper'
    def getname(self): return 'Flipper Music Format'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'track_lanes': False,
        'placement_cut': False,
        'placement_loop': False,
        'track_nopl': True
        }
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(30)
        if bytesdata == b'Filetype: Flipper Music Format': return True
        else: return False
    def parse(self, input_file, extra_param):

        l_key = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        fmf_BPM = 120
        fmf_Duration = 4
        fmf_Octave = 5
        Notes = []

        totalDuration = 0

        f_fmf = open(input_file, 'r')
        lines_fmf = f_fmf.readlines()
        for line in lines_fmf:
            if line != "\n":
                fmf_command, fmf_param = line.rstrip().split(': ')
                if fmf_command == 'BPM': fmf_BPM = int(fmf_param)
                if fmf_command == 'Duration': fmf_Duration = int(fmf_param)
                if fmf_command == 'Octave': fmf_Octave = int(fmf_param)
                if fmf_command == 'Notes':
                    fmf_notes = fmf_param.split(',')
                    for fmf_note in fmf_notes:
                        nospacenote = fmf_note.strip()
                        part_Note = ''
                        part_Duration = ''
                        part_Oct = ''
                        part_Period = 0
                        number_parsemode = 'D'
                        for notepart in nospacenote:
                            #print(notepart, end='')
                            if number_parsemode == 'D':
                                if notepart.isalpha() == False: part_Duration += notepart
                                if notepart == "#":
                                    part_Note += notepart
                                if notepart.isalpha() == True:
                                    part_Note += notepart
                                    number_parsemode = 'O'
                            if number_parsemode == 'O':
                                if notepart == "#": part_Note += notepart
                                if notepart.isnumeric() == True: part_Oct += notepart
                                if notepart == '.': part_Period += 1
                        
                        output_Oct = (fmf_Octave-5)*12 if part_Oct == '' else (int(part_Oct)-5)*12
                        output_Note = l_key.index(part_Note)+output_Oct if part_Note in l_key else  None
                        output_Duration = (fmf_Duration/16)/8 if part_Duration == '' else (fmf_Duration*(1/int(part_Duration)))/8

                        Notes.append([output_Note, output_Duration])

        notelist = []

        position = 0
        for Note in Notes:
            n_d = Note[1]*fmf_Duration
            n_k = Note[0]
            totalDuration += n_d
            if n_k != None: notelist.append( note_data.rx_makenote(position, n_d, n_k, None, None) )
            position += n_d

        cvpj_l = {}

        tracks_r.track_create(cvpj_l, 'flipperzero', 'instrument')
        tracks_r.track_visual(cvpj_l, 'flipperzero', name='Flipper Zero', color=[0.94, 0.58, 0.23])
        tracks_r.add_pl(cvpj_l, 'flipperzero', 'notes', placement_data.nl2pl(notelist))

        cvpj_l['do_singlenotelistcut'] = True

        song.add_param(cvpj_l, 'bpm', fmf_BPM)

        return json.dumps(cvpj_l)

