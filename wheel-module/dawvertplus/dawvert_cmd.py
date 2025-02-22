# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import argparse
import os
from dawvertplus.functions import core
from dawvertplus.functions import folder_samples
from dawvertplus.functions import plug_conv

print('DawVert: Daw Conversion Tool')

parser = argparse.ArgumentParser()
parser.add_argument("-i", default=None)
parser.add_argument("-it", default=None)
parser.add_argument("-o", default=None)
parser.add_argument("-ot", default=None)
parser.add_argument("--samplefolder", default=None)
parser.add_argument("--soundfont", default=None)
parser.add_argument("--songnum", default=1)
parser.add_argument("--extrafile", default=None)
parser.add_argument("--use-experiments-input", action='store_true')
parser.add_argument("--mi2m--output-unused-nle", action='store_true')
parser.add_argument("--nonfree-plugins", action='store_true')
parser.add_argument("--shareware-plugins", action='store_true')
parser.add_argument("-y", action='store_true')
args = parser.parse_args()

in_file = args.i
out_file = args.o
in_format = args.it
out_format = args.ot

if not os.path.exists(in_file):
	print('[error] Input File Not Found.')
	exit()

extra_json = {}
do_overwrite = False
pluginset = 'main'
dawvert_core = core.core() 

if args.y == True: do_overwrite = True
if args.soundfont != None: extra_json['soundfont'] = args.soundfont
if args.songnum != None: extra_json['songnum'] = args.songnum
if args.extrafile != None: extra_json['extrafile'] = args.extrafile
if args.mi2m__output_unused_nle == True: extra_json['mi2m-output-unused-nle'] = True
if args.use_experiments_input == True: 
	extra_json['use_experiments_input'] = True
	pluginset = 'experiments'

if args.nonfree_plugins == True: extra_json['nonfree-plugins'] = True
if args.shareware_plugins == True: extra_json['shareware-plugins'] = True


# -------------------------------------------------------------- Input Plugin List--------------------------------------------------------------
dawvert_core.input_load_plugins(pluginset)#mainかexperimentsか
plug_conv.load_plugins()

# -------------------------------------------------------------- Output Plugin List -------------------------------------------------------------
dawvert_core.output_load_plugins()

# -------------------------------------------------------------- Input Format--------------------------------------------------------------

if in_format == None:
	detect_plugin_found = dawvert_core.input_autoset(in_file)
	if detect_plugin_found == None:
		print('[error] could not identify the input format')
		exit()
else:
	if in_format in dawvert_core.input_get_plugins():
		in_class = dawvert_core.input_set(in_format)
	else:
		print('[error] input format plugin not found')
		exit()

# -------------------------------------------------------------- Output Format --------------------------------------------------------------

out_file_nameext = os.path.splitext(os.path.basename(out_file))
out_file_path = os.path.dirname(out_file)

if out_format in dawvert_core.output_get_plugins():
	out_class = dawvert_core.output_set(out_format)
else:
	print('[error] output format plugin not found')
	exit()

out_plug_ext = dawvert_core.output_get_extension()
if out_file_nameext[1] == '': out_file = os.path.join(out_file_path, out_file_nameext[0]+'.'+out_plug_ext)

# -------------------------------------------------------------- convert --------------------------------------------------------------

file_name = os.path.splitext(os.path.basename(in_file))[0]
if args.samplefolder != None:
	extra_json['samplefolder'] = args.samplefolder
else:
	extra_json['samplefolder'] = os.getcwd() + '/__extracted_samples/' + file_name + '/'

# -------------------------------------------------------------- convert --------------------------------------------------------------

if os.path.isfile(out_file) and do_overwrite == False:
	user_input = input("File '"+out_file+"' already exists. Overwrite? [y/n]")
	if user_input.lower() == 'y': pass
	elif user_input.lower() == 'n': exit()
	else: 
		print('Not overwriting - exiting')
		exit()

dawvert_core.parse_input(in_file, extra_json)
dawvert_core.convert_type_output(extra_json)
dawvert_core.convert_plugins(extra_json)
dawvert_core.parse_output(out_file)