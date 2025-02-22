# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dawvertplus.plugin_input import base
import json
from mido import MidiFile
from dawvertplus.functions_plugin import format_midi_in
#from dawvertplus.functions import infofinder
#from dawvertplus.functions import midi_exdata
#from dawvertplus.functions import colors
#from dawvertplus.functions import song

class input_midi(base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'midi'
    def getname(self): return 'MIDI'
    def gettype(self): return 'rm'
    def getdawcapabilities(self): 
        return {
        'fxrack': True,
        'fxrack_params': [],
        'auto_nopl': True, 
        'track_nopl': True}
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'MThd': return True
        else: return False
    def parse(self, input_file, extra_param):

        midifile = MidiFile(input_file, clip=True)
        ppq = midifile.ticks_per_beat
        print("[input-midi] PPQ: " + str(ppq))

        num_tracks = len(midifile.tracks)
        songdescline = []
        midi_copyright = None

        format_midi_in.song_start(16, ppq, num_tracks, 120, [4,4])

        t_tracknames = []

        for track in midifile.tracks:
            midi_trackname = None

            timepos = 0

            midicmds = []

            for msg in track:
                midicmds.append(['rest', msg.time])

                if msg.type == 'note_on':
                    if msg.velocity != 0: midicmds.append(['note_on', msg.channel, msg.note, msg.velocity])
                    else: midicmds.append(['note_off', msg.channel, msg.note])
                elif msg.type == 'note_off': midicmds.append(['note_off', msg.channel, msg.note])
                elif msg.type == 'pitchwheel': midicmds.append(['pitchwheel', msg.channel, (msg.pitch/4096)])
                elif msg.type == 'program_change': midicmds.append(['program_change', msg.channel, msg.program])
                elif msg.type == 'control_change': midicmds.append(['control_change', msg.channel, msg.control, msg.value])
                elif msg.type == 'set_tempo': midicmds.append(['tempo', 60000000/msg.tempo])
                elif msg.type == 'time_signature': midicmds.append(['timesig', msg.numerator, msg.denominator])
                elif msg.type == 'marker': midicmds.append(['marker', msg.text])
                elif msg.type == 'text': midicmds.append(['text', msg.text])
                elif msg.type == 'sysex': midicmds.append(['sysex', msg.data])
                elif msg.type == 'key_signature': midicmds.append(['key_signature', msg.key])
                elif msg.type == 'track_name': midicmds.append(['track_name', msg.name])
                elif msg.type == 'sequencer_specific': midicmds.append(['sequencer_specific', msg.data])
                elif msg.type == 'copyright': midicmds.append(['copyright', msg.text])
                #selif msg.type == 'end_of_track': midicmds.append(['end_of_track'])

            format_midi_in.add_track(0, midicmds)

        cvpj_l = {}

        format_midi_in.song_end(cvpj_l)

        cvpj_l['do_addloop'] = True
        cvpj_l['do_singlenotelistcut'] = True
        
        #cvpj_l['timesig'] = s_timesig
        #song.add_param(cvpj_l, 'bpm', s_tempo)

        #author = infofinder.author

        #if midi_copyright != None and author == None:
        #    song.add_info(cvpj_l, 'author', midi_copyright)
        #    infofinder.getinfo(cvpj_l, midi_copyright)

        #for t_trackname in t_tracknames:
        #    infofinder.getinfo(cvpj_l, t_trackname)

        #for songdesc in songdescline:
        #    song_message = song_message+songdesc+'\n'

        #if num_tracks != 1: song.add_info_msg(cvpj_l, 'text', song_message)
        #elif midi_trackname != None: song.add_info(cvpj_l, 'title', midi_trackname)

        return json.dumps(cvpj_l)
