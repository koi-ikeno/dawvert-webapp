# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

#import math
import json
import os
#import base64
import lxml.etree as ET
from xml.dom import minidom

from dawvertplus.functions import colors
from dawvertplus.functions import notelist_data
#from dawvertplus.functions import data_bytes
from dawvertplus.functions import data_values
from dawvertplus.functions import auto
from dawvertplus.functions import audio
from dawvertplus.functions import plugins
from dawvertplus.functions import params
from dawvertplus.functions import song
from dawvertplus.functions import data_dataset
#from dawvertplus.functions_plugin import ableton_values
from dawvertplus.functions_tracks import tracks_r
from dawvertplus.plugin_output import base


colorlist = ['FF94A6','FFA529','CC9927','F7F47C','BFFB00','1AFF2F','25FFA8','5CFFE8','8BC5FF','5480E4','92A7FF','D86CE4','E553A0','FFFFFF','FF3636','F66C03','99724B','FFF034','87FF67','3DC300','00BFAF','19E9FF','10A4EE','007DC0','886CE4','B677C6','FF39D4','D0D0D0','E2675A','FFA374','D3AD71','EDFFAE','D2E498','BAD074','9BC48D','D4FDE1','CDF1F8','B9C1E3','CDBBE4','AE98E5','E5DCE1','A9A9A9','C6928B','B78256','99836A','BFBA69','A6BE00','7DB04D','88C2BA','9BB3C4','85A5C2','8393CC','A595B5','BF9FBE','BC7196','7B7B7B','AF3333','A95131','724F41','DBC300','85961F','539F31','0A9C8E','236384','1A2F96','2F52A2','624BAD','A34BAD','CC2E6E','3C3C3C']
colorlist_one = [colors.hex_to_rgb_float(color) for color in colorlist]
 
delaytime = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 4],
    [4, 5],
    [5, 6],
    [6, 8],
    [7, 16],
    ]
# ---------------------------------------------- Functions Main ----------------------------------------------
# ---------  Main  ---------

counter_unused_id = data_values.counter(500000)
counter_pointee = data_values.counter(400000)
counter_cont = data_values.counter(300000)
counter_clip = data_values.counter(0)
counter_keytrack = data_values.counter(-1)
counter_note = data_values.counter(0)

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

abl_bool_val = ['false','true']

def makevaltype(value, valtype):
    if valtype != None:
        if valtype == 'bool': 
            if isinstance(value, bool): return abl_bool_val[bool(value)]
            else: return value
        elif valtype == 'float': return float(value)
        elif valtype == 'int': return str(int(value))
        else: return str(value)
    return valtype

def addvalue(xmltag, name, value):
    x_temp = ET.SubElement(xmltag, name)
    x_temp.set('Value', str(value))
    return x_temp

def addvalue_nosub(name, value):
    x_temp = ET.Element(name)
    x_temp.set('Value', str(value))
    return x_temp

def addhex(xmltag, name, bytesdata):
    hexbuffer = ''.join('{:02X}'.format(x) for x in bytesdata)
    x_temp = ET.SubElement(xmltag, name)
    x_temp.text = '\n' + '\n'.join(data_values.list_chunks(hexbuffer, 80))

def addLomId(xmltag, name, value):
    x_temp = ET.SubElement(xmltag, name)
    x_temp.set('LomId', value)
    return x_temp
      
def addId(xmltag, name, value):
    x_temp = ET.SubElement(xmltag, name)
    x_temp.set('Id', value)
    return x_temp
      
def add_up_lower(xmltag, name, target, upper, lower):
    x_temp = ET.SubElement(xmltag, name)
    addvalue(x_temp, 'Target', target)
    addvalue(x_temp, 'UpperDisplayString', upper)
    addvalue(x_temp, 'LowerDisplayString', lower)
    return x_temp
      
def add_min_max(xmltag, name, imin, imax, isint):
    x_temp = ET.SubElement(xmltag, name)
    if isint:
        addvalue(x_temp, 'Min', str(int(imin)))
        addvalue(x_temp, 'Max', str(int(imax)))
    else:
        addvalue(x_temp, 'Min', str(imin))
        addvalue(x_temp, 'Max', str(imax))
    return x_temp
      
def set_add_VideoWindowRect(xmltag):
    x_temp = ET.SubElement(xmltag, 'VideoWindowRect')
    x_temp.set('Top', '-2147483648')
    x_temp.set('Left', '-2147483648')
    x_temp.set('Bottom', '-2147483648')
    x_temp.set('Right', '-2147483648')

def add_xyval(xmltag, x_name, x_x, x_y):
    x_SessionScrollerPos = ET.SubElement(xmltag, x_name)
    x_SessionScrollerPos.set('X', str(x_x))
    x_SessionScrollerPos.set('Y', str(x_y))
#
def create_FollowAction(xmltag, FTime, Linked, LoopIter, FollowAct, FollowCha, JumpIndex, FollowEnabled):
    x_FollowAction = ET.SubElement(xmltag, 'FollowAction')
    addvalue(x_FollowAction, 'FollowTime', str(FTime))
    addvalue(x_FollowAction, 'IsLinked', Linked)
    addvalue(x_FollowAction, 'LoopIterations', str(LoopIter))
    addvalue(x_FollowAction, 'FollowActionA', str(FollowAct[0]))
    addvalue(x_FollowAction, 'FollowActionB', str(FollowAct[1]))
    addvalue(x_FollowAction, 'FollowChanceA', str(FollowCha[0]))
    addvalue(x_FollowAction, 'FollowChanceB', str(FollowCha[1]))
    addvalue(x_FollowAction, 'JumpIndexA', str(JumpIndex[0]))
    addvalue(x_FollowAction, 'JumpIndexB', str(JumpIndex[1]))
    addvalue(x_FollowAction, 'FollowActionEnabled', FollowEnabled)

def create_Locators(xmltag):
    x_temp = ET.SubElement(xmltag, 'Locators')
    x_Locators = ET.SubElement(x_temp, 'Locators')
    return x_Locators
    
def create_Scenes(xmltag):
    x_Scenes = ET.SubElement(xmltag, 'Scenes')
    for scenenum in range(8):
        x_Scene = addId(x_Scenes, 'Scene', str(scenenum))
        create_FollowAction(x_Scene, 4, 'true', 1, [4,0], [100,0], [0,0], 'false')
        addvalue(x_Scene, 'Name', "")
        addvalue(x_Scene, 'Annotation', "")
        addvalue(x_Scene, 'Color', "-1")
        addvalue(x_Scene, 'Tempo', "120")
        addvalue(x_Scene, 'IsTempoEnabled', "false")
        addvalue(x_Scene, 'TimeSignatureId', "201")
        addvalue(x_Scene, 'IsTimeSignatureEnabled', "false")
        addvalue(x_Scene, 'LomId', "0")
        addLomId(x_Scene, 'ClipSlotsListWrapper', "0")

ExpressionLaneNum = 0

def create_ExpressionLanes(xmltag):
    global ExpressionLaneNum
    x_ExpressionLanes = ET.SubElement(xmltag, 'ExpressionLanes')
    for lanenum in range(4):
        x_ExpressionLane = addId(x_ExpressionLanes, 'ExpressionLane', str(lanenum))
        addvalue(x_ExpressionLane, 'Type', str(ExpressionLaneNum))
        addvalue(x_ExpressionLane, 'Size', '41')
        addvalue(x_ExpressionLane, 'IsMinimized', 'true')
        ExpressionLaneNum += 1

def create_ContentLanes(xmltag):
    global ExpressionLaneNum
    x_ContentLanes = ET.SubElement(xmltag, 'ContentLanes')
    for lanenum in range(2):
        x_ExpressionLane = addId(x_ContentLanes, 'ExpressionLane', str(lanenum))
        addvalue(x_ExpressionLane, 'Type', str(ExpressionLaneNum))
        addvalue(x_ExpressionLane, 'Size', '41')
        addvalue(x_ExpressionLane, 'IsMinimized', 'true')
        ExpressionLaneNum += 1

def create_grid(xmltag, xmlname, FixedNumerator, FixedDenominator, GridIntervalPixel, Ntoles, SnapToGrid, Fixed):
    x_Grid = ET.SubElement(xmltag, xmlname)
    addvalue(x_Grid, 'FixedNumerator', str(FixedNumerator))
    addvalue(x_Grid, 'FixedDenominator', str(FixedDenominator))
    addvalue(x_Grid, 'GridIntervalPixel', str(GridIntervalPixel))
    addvalue(x_Grid, 'Ntoles', str(Ntoles))
    addvalue(x_Grid, 'SnapToGrid', str(SnapToGrid))
    addvalue(x_Grid, 'Fixed', str(Fixed))

def create_transport(xmltag, loopstart, looplen, Loopon):
    x_Transport = ET.SubElement(xmltag, 'Transport')
    addvalue(x_Transport, 'PhaseNudgeTempo', '10')
    addvalue(x_Transport, 'LoopOn', str(Loopon))
    addvalue(x_Transport, 'LoopStart', str(loopstart))
    addvalue(x_Transport, 'LoopLength', str(looplen))
    addvalue(x_Transport, 'LoopIsSongStart', 'false')
    addvalue(x_Transport, 'CurrentTime', '0')
    addvalue(x_Transport, 'PunchIn', 'false')
    addvalue(x_Transport, 'PunchOut', 'false')
    addvalue(x_Transport, 'MetronomeTickDuration', '0')
    addvalue(x_Transport, 'DrawMode', 'false')

def create_GroovePool(xmltag):
    x_temp = ET.SubElement(xmltag, 'GroovePool')
    addvalue(x_temp, 'LomId', '0')
    ET.SubElement(x_temp, 'Grooves')
    
def create_AutoColorPickerForPlayerAndGroupTracks(xmltag):
    x_temp = ET.SubElement(xmltag, 'AutoColorPickerForPlayerAndGroupTracks')
    addvalue(x_temp, 'NextColorIndex', '15')
    
def create_AutoColorPickerForReturnAndMasterTracks(xmltag):
    x_temp = ET.SubElement(xmltag, 'AutoColorPickerForReturnAndMasterTracks')
    addvalue(x_temp, 'NextColorIndex', '14')

def create_scaleinformation(xmltag):
    x_ScaleInformation = ET.SubElement(xmltag, 'ScaleInformation')
    addvalue(x_ScaleInformation, 'RootNote', '0')
    addvalue(x_ScaleInformation, 'Name', 'Major')

def create_songmastervalues(xmltag):
    x_SongMasterValues = ET.SubElement(xmltag, 'SongMasterValues')
    add_xyval(x_SongMasterValues, 'SessionScrollerPos', 0, 0)

def create_sequencernavigator(xmltag):
    x_SequencerNavigator = ET.SubElement(xmltag, 'SequencerNavigator')
    x_BeatTimeHelper = ET.SubElement(x_SequencerNavigator, 'BeatTimeHelper')
    addvalue(x_BeatTimeHelper, 'CurrentZoom', '0.08')
    add_xyval(x_SequencerNavigator, 'ScrollerPos', 0, 0)
    add_xyval(x_SequencerNavigator, 'ClientSize', 888, 587)

def create_viewstates(xmltag):
    x_Transport = ET.SubElement(xmltag, 'ViewStates')
    addvalue(x_Transport, 'SessionIO', '1')
    addvalue(x_Transport, 'SessionSends', '1')
    addvalue(x_Transport, 'SessionReturns', '1')
    addvalue(x_Transport, 'SessionMixer', '1')
    addvalue(x_Transport, 'SessionTrackDelay', '0')
    addvalue(x_Transport, 'SessionCrossFade', '0')
    addvalue(x_Transport, 'SessionShowOverView', '0')
    addvalue(x_Transport, 'ArrangerIO', '1')
    addvalue(x_Transport, 'ArrangerReturns', '1')
    addvalue(x_Transport, 'ArrangerMixer', '1')
    addvalue(x_Transport, 'ArrangerTrackDelay', '0')
    addvalue(x_Transport, 'ArrangerShowOverView', '1')

def create_timeselection(xmltag, AnchorTime, OtherTime):
    x_Transport = ET.SubElement(xmltag, 'TimeSelection')
    addvalue(x_Transport, 'AnchorTime', str(AnchorTime))
    addvalue(x_Transport, 'OtherTime', str(OtherTime))

def add_env_target(xmltag, i_name, i_id):
    x_temp = addId(xmltag, i_name, str(i_id))
    addvalue(x_temp, 'LockEnvelope', '0')

def dictxmlk(xmltag, i_dict):
    for key, value in i_dict.items():
        if not isinstance(value, dict):
            xmltag.append(value)
        else:
            x_temp = ET.SubElement(xmltag, key)
            dictxmlk(x_temp, value)

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------- Device Param/Data --------------------------------------------------------------

def create_SampleParts(x_SampleParts, cvpj_samplepart, idnum):
    try:
        samplefilepath = cvpj_samplepart['file']
        aud_sampledata = audio.get_audiofile_info(samplefilepath)

        samp_start = 0
        samp_vol = cvpj_samplepart['vol'] if 'vol' in cvpj_samplepart else 1
        samp_pan = cvpj_samplepart['pan'] if 'pan' in cvpj_samplepart else 0
        samp_loop_enabled = 0
        samp_loop_start = 0
        samp_loop_keyr = [0, 127]
        samp_loop_velr = [1, 127]
        samp_loop_root = cvpj_samplepart['middlenote']+60 if 'middlenote' in cvpj_samplepart else 60
        samp_point_value_type = cvpj_samplepart['point_value_type'] if 'point_value_type' in cvpj_samplepart else 'percent'

        if 'r_key' in cvpj_samplepart: 
            keyrange = cvpj_samplepart['r_key']
            samp_loop_keyr = [keyrange[0]+60, keyrange[1]+60]

        samp_end = cvpj_samplepart['length'] if 'length' in cvpj_samplepart else aud_sampledata['dur']
        samp_loop_end = samp_end

        if 'loop' in cvpj_samplepart: 
            loopdata = cvpj_samplepart['loop']
            if 'enabled' in loopdata: 
                if loopdata['enabled'] == 1:
                    samp_loop_enabled = 1
                    if 'points' in loopdata:
                        if samp_point_value_type == 'samples':
                            samp_loop_start = loopdata['points'][0]
                            samp_loop_end = loopdata['points'][1]
                        else:
                            samp_loop_start = loopdata['points'][0]*samp_end
                            samp_loop_end = loopdata['points'][1]*samp_end

        x_MultiSamplePart = ET.SubElement(x_SampleParts, 'MultiSamplePart')
        x_MultiSamplePart.set('Id', str(idnum))
        x_MultiSamplePart.set('HasImportedSlicePoints', 'false')
        x_MultiSamplePart.set('NeedsAnalysisData', 'false')
        addvalue(x_MultiSamplePart, 'LomId', '0')
        addvalue(x_MultiSamplePart, 'Selection', 'true')
        addvalue(x_MultiSamplePart, 'IsActive', 'true')
        addvalue(x_MultiSamplePart, 'Solo', 'false')
        add_range_val(x_MultiSamplePart, 'KeyRange', samp_loop_keyr[0], samp_loop_keyr[1], samp_loop_keyr[0], samp_loop_keyr[1])
        add_range_val(x_MultiSamplePart, 'VelocityRange', samp_loop_velr[0], samp_loop_velr[1], samp_loop_velr[0], samp_loop_velr[1])
        add_range_val(x_MultiSamplePart, 'SelectorRange', 0, 127, 0, 127)
        addvalue(x_MultiSamplePart, 'RootKey', samp_loop_root)
        addvalue(x_MultiSamplePart, 'Detune', '0')
        addvalue(x_MultiSamplePart, 'TuneScale', '100')
        addvalue(x_MultiSamplePart, 'Panorama', samp_pan)
        addvalue(x_MultiSamplePart, 'Volume', samp_vol)
        addvalue(x_MultiSamplePart, 'Link', 'false')
        addvalue(x_MultiSamplePart, 'SampleStart', samp_start)
        addvalue(x_MultiSamplePart, 'SampleEnd', samp_end)
        x_SustainLoop = ET.SubElement(x_MultiSamplePart, 'SustainLoop')
        addvalue(x_SustainLoop, 'Start', samp_loop_start)
        addvalue(x_SustainLoop, 'End', samp_loop_end)
        addvalue(x_SustainLoop, 'Mode', samp_loop_enabled)
        addvalue(x_SustainLoop, 'Crossfade', '0')
        addvalue(x_SustainLoop, 'Detune', '0')
        x_ReleaseLoop = ET.SubElement(x_MultiSamplePart, 'ReleaseLoop')
        addvalue(x_ReleaseLoop, 'Start', samp_loop_start)
        addvalue(x_ReleaseLoop, 'End', samp_loop_end)
        addvalue(x_ReleaseLoop, 'Mode', '0')
        addvalue(x_ReleaseLoop, 'Crossfade', '0')
        addvalue(x_ReleaseLoop, 'Detune', '0')

        create_sampleref(x_MultiSamplePart, aud_sampledata, None)
    except:
        pass

def add_range_val(xmltag, name, low_range, hi_range, low_cr_range, hi_cr_range):
    x_subtag = ET.SubElement(xmltag, name)
    addvalue(x_subtag, 'Min', str(low_range))
    addvalue(x_subtag, 'Max', str(hi_range))
    addvalue(x_subtag, 'CrossfadeMin', str(low_cr_range))
    addvalue(x_subtag, 'CrossfadeMax', str(hi_cr_range))

def do_device_data_intro(xmltag, deviceid, ableton_devicename, fx_on, fx_name):
    xml_device = ET.SubElement(xmltag, ableton_devicename)
    xml_device.set('Id', str(deviceid))
    addvalue(xml_device, 'LomId', '0')
    addvalue(xml_device, 'LomIdView', '0')
    addvalue(xml_device, 'IsExpanded', 'false')
    set_add_param(xml_device, 'On', fx_on, str(counter_unused_id.get()), None, [64,127], None)
    addvalue(xml_device, 'ModulationSourceCount', '0')
    addLomId(xml_device, 'ParametersListWrapper', '0')
    addId(xml_device, 'Pointee', str(counter_pointee.get()))
    addvalue(xml_device, 'LastSelectedTimeableIndex', '0')
    addvalue(xml_device, 'LastSelectedClipEnvelopeIndex', '0')
    x_LastPresetRef = ET.SubElement(xml_device, 'LastPresetRef')
    x_LastPresetRef_Value = ET.SubElement(x_LastPresetRef, 'Value')
    x_LockedScripts = ET.SubElement(xml_device, 'LockedScripts')
    addvalue(xml_device, 'IsFolded', 'false')
    addvalue(xml_device, 'ShouldShowPresetName', 'false')
    addvalue(xml_device, 'UserName', fx_name)
    addvalue(xml_device, 'Annotation', '')
    x_SourceContext = ET.SubElement(xml_device, 'SourceContext')
    x_SourceContext_Value = ET.SubElement(x_SourceContext, 'Value')
    return xml_device


def do_device_data_single(cvpj_plugindata, xmltag, deviceid, pluginid, is_instrument):
    plugtype = cvpj_plugindata.type_get()

    if plugtype in [['sampler', 'single'], ['sampler', 'multi']]:
        xml_device = do_device_data_intro(xmltag, deviceid, 'MultiSampler', True, '')

        sampleidnum = 0

        if plugtype[1] in ['single', 'multi']:
            x_Player = ET.SubElement(xml_device, 'Player')
            cvpj_regions = cvpj_plugindata.regions_get()

            x_MultiSampleMap = ET.SubElement(x_Player, 'MultiSampleMap')
            addvalue(x_MultiSampleMap, 'LoadInRam', 'false')
            addvalue(x_MultiSampleMap, 'LayerCrossfade', '0')
            x_SampleParts = ET.SubElement(x_MultiSampleMap, 'SampleParts')

            if plugtype[1] == 'single':
                cvpj_region = {}
                cvpj_region['vol'] = cvpj_plugindata.dataval_get('vol', 1)
                cvpj_region['pan'] = cvpj_plugindata.dataval_get('pan', 0)
                cvpj_region['middlenote'] = cvpj_plugindata.dataval_get('middlenote', 0)
                cvpj_region['point_value_type'] = cvpj_plugindata.dataval_get('point_value_type', 'samples')
                cvpj_region['start'] = cvpj_plugindata.dataval_get('start', 0)
                cvpj_region['loop'] = cvpj_plugindata.dataval_get('loop', {})
                cvpj_region['file'] = cvpj_plugindata.dataval_get('file', '')
                create_SampleParts(x_SampleParts, cvpj_region, sampleidnum)

            if plugtype[1] == 'multi':
                cvpj_regions = cvpj_plugindata.regions_get()
                if cvpj_regions:
                    for cvpj_region in cvpj_regions:
                        create_SampleParts(x_SampleParts, cvpj_region, sampleidnum)
                        sampleidnum += 1

            set_add_param(x_Player, 'Reverse', False, str(counter_unused_id.get()), None, [64,127], None)
            set_add_param(x_Player, 'Snap', False, str(counter_unused_id.get()), None, [64,127], None)
            set_add_param(x_Player, 'SampleSelector', 0, str(counter_unused_id.get()), None, None, None)
            addvalue(x_Player, 'InterpolationMode', '1')
            addvalue(x_Player, 'UseConstPowCrossfade', 'true')

    if plugtype[0] in ['native-ableton']:
        devicename = plugtype[1]
        paramlist = dataset.params_list('plugin', devicename)

        if paramlist:
            print('[output-ableton] Device:', devicename)

            fx_on, fx_wet = cvpj_plugindata.fxdata_get()
            fx_name, fx_color = cvpj_plugindata.fxvisual_get()
            if fx_name == None: fx_name = ''

            xml_device = do_device_data_intro(xmltag, deviceid, devicename, fx_on, fx_name)

            if devicename not in ['MultiSampler', 'OriginalSimpler']:
                paramgroups = []
                paramdat = {}
 
                #data_values.nested_dict_add_value(paramdat, paramgroup, {})

                paramlist = dataset.params_list('plugin', devicename)
                for paramid in paramlist:
                    paramdata = dataset.params_i_get('plugin', devicename, paramid)
                    paramnamesplit = paramid.split('/')

                    if paramdata[0] == False:
                        cvpj_paramval = cvpj_plugindata.param_get(paramid, paramdata[2])[0]
                        midi_minmax = paramdata[3:5] if paramdata[3:5] != [None, None] else None
                        elementdata = set_add_param_nosub(
                            paramnamesplit[-1], 
                            makevaltype(cvpj_paramval, paramdata[1]), 
                            None, None, None, midi_minmax)
                        data_values.nested_dict_add_value(paramdat, paramid.split('/'), elementdata)
                    else:
                        cvpj_paramval = cvpj_plugindata.dataval_get(paramid, paramdata[2])
                        if paramdata[1] != 'list':
                            elementdata = addvalue_nosub(paramnamesplit[-1], makevaltype(cvpj_paramval, paramdata[1]))
                            data_values.nested_dict_add_value(paramdat, paramid.split('/'), elementdata)
                        else:
                            for index, listpart in enumerate(cvpj_paramval):
                                tempsplit = paramnamesplit.copy()
                                tempsplit[-1] += '.'+str(index)
                                elementdata = addvalue_nosub(tempsplit[-1], str(listpart))
                                data_values.nested_dict_add_value(paramdat, tempsplit, elementdata)

                dictxmlk(xml_device, paramdat)

                if devicename == 'Looper':
                    addhex(xml_device, 'SavedBuffer', cvpj_plugindata.rawdata_get())
                    
                if devicename == 'Hybrid':
                    samplefilepath = cvpj_plugindata.dataval_get('sample', '')
                    samplerefdict = {}
                    samplerefdict['path'] = samplefilepath
                    aud_sampledata = audio.get_audiofile_info(samplefilepath)

                    x_ImpulseResponseHandler = ET.SubElement(xml_device, 'ImpulseResponseHandler')
                    x_SampleSlot = ET.SubElement(x_ImpulseResponseHandler, 'SampleSlot')
                    x_SampleSlotValue = ET.SubElement(x_SampleSlot, 'Value')
                    x_SampleSlotTrueStereo = ET.SubElement(x_ImpulseResponseHandler, 'SampleSlotTrueStereo')
                    x_SampleSlotTrueStereoValue = ET.SubElement(x_SampleSlotTrueStereo, 'Value')
                    create_sampleref(x_SampleSlotValue, aud_sampledata, 3)

                if devicename == 'InstrumentVector':
                    x_ModulationConnections = ET.SubElement(xml_device, 'ModulationConnections')
                    d_ModulationConnections = cvpj_plugindata.dataval_get('ModulationConnections', [])
                    modconid = 0

                    for d_ModulationConnection in d_ModulationConnections:
                        x_ModulationConnectionsForInstrumentVector = ET.SubElement(x_ModulationConnections, 'ModulationConnectionsForInstrumentVector')
                        x_ModulationConnectionsForInstrumentVector.set('Id', str(modconid))
                        x_ModulationConnectionsForInstrumentVector.set('TargetId', d_ModulationConnection['target'])
                        addvalue(x_ModulationConnectionsForInstrumentVector, 'TargetName', d_ModulationConnection['name'])
                        for num in range(13):
                            addvalue(x_ModulationConnectionsForInstrumentVector, 
                                'ModulationAmounts.'+str(num), 
                                str(d_ModulationConnection['amounts'][num])
                             )
                        modconid += 1

                    d_UserSprite1 = cvpj_plugindata.dataval_get('UserSprite1', '')
                    d_UserSprite2 = cvpj_plugindata.dataval_get('UserSprite2', '')

                    x_UserSprite1 = ET.SubElement(xml_device, 'UserSprite1')
                    x_UserSprite1Value = ET.SubElement(x_UserSprite1, 'Value')
                    if d_UserSprite1 != '':
                        aud_sampledata_UserSprite1 = audio.get_audiofile_info(d_UserSprite1)
                        create_sampleref(x_UserSprite1Value, aud_sampledata_UserSprite1, '1')

                    x_UserSprite2 = ET.SubElement(xml_device, 'UserSprite2')
                    x_UserSprite2Value = ET.SubElement(x_UserSprite2, 'Value')
                    if d_UserSprite2 != '':
                        aud_sampledata_UserSprite2 = audio.get_audiofile_info(d_UserSprite2)
                        create_sampleref(x_UserSprite2Value, aud_sampledata_UserSprite2, '2')

    if plugtype[0] in ['vst2']:
        if plugtype[0] == 'vst2':
            fx_on, fx_wet = cvpj_plugindata.fxdata_get()
            fx_name, fx_color = cvpj_plugindata.fxvisual_get()
            xml_device = do_device_data_intro(xmltag, deviceid, 'PluginDevice', fx_on, fx_name)
            x_PluginDesc = ET.SubElement(xml_device, 'PluginDesc')
            x_VstPluginInfo = addId(x_PluginDesc, 'VstPluginInfo', '0')
            vst_pos, vst_size, vst_open, vst_max = song.get_visual_window(cvpj_l, 'plugin', pluginid, [0,0], None, False, False)
            if vst_pos != None:
                addvalue(x_VstPluginInfo, 'WinPosX', vst_pos[0])
                addvalue(x_VstPluginInfo, 'WinPosY', vst_pos[1])

            vstpath = cvpj_plugindata.dataval_get('path', '')
            vstname = os.path.basename(vstpath).split('.')[0]
            vstid = cvpj_plugindata.dataval_get('fourid', 0)
            vstversion = cvpj_plugindata.dataval_get('version_bytes', 0)
            vstnumparams = cvpj_plugindata.dataval_get('numparams', None)
            current_program = cvpj_plugindata.dataval_get('current_program', 0)

            vstdatatype = cvpj_plugindata.dataval_get('datatype', 'chunk')

            if vstnumparams == None: vstnumparams = len(cvpj_plugindata.param_list())

            addvalue(x_VstPluginInfo, 'Path', vstpath)
            addvalue(x_VstPluginInfo, 'PlugName', vstname)
            addvalue(x_VstPluginInfo, 'UniqueId', vstid)
            addvalue(x_VstPluginInfo, 'Inputs', 0)
            addvalue(x_VstPluginInfo, 'Outputs', 0)
            addvalue(x_VstPluginInfo, 'NumberOfParameters', vstnumparams)
            addvalue(x_VstPluginInfo, 'NumberOfPrograms', 1)

            if vstdatatype == 'chunk': outflags = 67110149 if is_instrument else 67110144
            else: outflags = 67108869 if is_instrument else 67109120

            addvalue(x_VstPluginInfo, 'Flags', outflags)
            x_Preset = ET.SubElement(x_VstPluginInfo, 'Preset')
            x_VstPreset = addId(x_Preset, 'VstPreset', "0")
            addvalue(x_VstPreset, 'OverwriteProtectionNumber', 2816)
            ET.SubElement(x_VstPreset, 'ParameterSettings')
            addvalue(x_VstPreset, 'IsOn', 'true')
            addvalue(x_VstPreset, 'PowerMacroControlIndex', -1)
            add_min_max(x_VstPreset, 'PowerMacroMappingRange', 64,127, False)

            addvalue(x_VstPreset, 'IsFolded', "false")
            addvalue(x_VstPreset, 'StoredAllParameters', "true")
            addvalue(x_VstPreset, 'DeviceLomId', 0)
            addvalue(x_VstPreset, 'DeviceViewLomId', 0)
            addvalue(x_VstPreset, 'IsOnLomId', 0)
            addvalue(x_VstPreset, 'ParametersListWrapperLomId', 0)
            addvalue(x_VstPreset, 'Type', 1178747752)
            addvalue(x_VstPreset, 'ProgramCount', 1)
            if vstnumparams != None: addvalue(x_VstPreset, 'ParameterCount', vstnumparams)
            addvalue(x_VstPreset, 'ProgramNumber', current_program)
            if vstdatatype == 'chunk': 
                rawdata = cvpj_plugindata.rawdata_get()
                addhex(x_VstPreset, 'Buffer', rawdata)
            addvalue(x_VstPreset, 'Name', '')
            addvalue(x_VstPreset, 'PluginVersion', vstversion)
            addvalue(x_VstPreset, 'UniqueId', vstid)
            addvalue(x_VstPreset, 'ByteOrder', 2)

            addvalue(x_VstPluginInfo, 'Version', vstversion)
            addvalue(x_VstPluginInfo, 'VstVersion', "2400")
            addvalue(x_VstPluginInfo, 'IsShellClient', "false")
            addvalue(x_VstPluginInfo, 'Category', 2 if is_instrument else 1)
            addvalue(x_VstPluginInfo, 'LastPresetFolder', "")

        addvalue(xml_device, 'MpeEnabled', 'false')
        x_ParameterList = ET.SubElement(xml_device, 'ParameterList')
        paramlist = cvpj_plugindata.param_list()
        for paramnum, paramid in enumerate(paramlist):
            if paramid[0:10] == 'ext_param_':
                paramidnum = int(paramid[10:].split('_')[0])

                cvpj_param = cvpj_plugindata.param_get(paramid, 0)

                x_PluginFloatParameter = addId(x_ParameterList, 'PluginFloatParameter', str(paramnum))
                addvalue(x_PluginFloatParameter, 'ParameterName', cvpj_param[2])
                addvalue(x_PluginFloatParameter, 'ParameterId', paramidnum)
                addvalue(x_PluginFloatParameter, 'VisualIndex', paramnum)
                set_add_param(x_PluginFloatParameter, 'ParameterValue', cvpj_param[0], None, None, None, [0,1])






def do_device_data_instrument(cvpj_track_data, xmltag):
    if 'instdata' in cvpj_track_data:
        if 'pluginid' in cvpj_track_data['instdata']:
            pluginid = cvpj_track_data['instdata']['pluginid']
            inst_plugindata = plugins.cvpj_plugin('cvpj', cvpj_l, pluginid)
            do_device_data_single(inst_plugindata, xmltag, 5, pluginid, True)

def do_device_data(cvpj_track_data, xmltag):
    ableton_deviceid = 6
    if 'chain_fx_audio' in cvpj_track_data:
        for fxpluginid in cvpj_track_data['chain_fx_audio']:
            inst_plugindata = plugins.cvpj_plugin('cvpj', cvpj_l, fxpluginid)
            do_device_data_single(inst_plugindata, xmltag, ableton_deviceid, fxpluginid, False)
            ableton_deviceid += 1





# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------- Track Base Data --------------------------------------------------------------

# ---------------- Device Chain / Mixer ----------------

def set_add_param(xmltag, param_name, param_value, auto_id, modu_id, midi_cc_thres, midi_cont_range):
    x_temp = ET.SubElement(xmltag, param_name)
    addvalue(x_temp, 'LomId', '0')
    if isinstance(param_value, bool): 
        if param_value: addvalue(x_temp, 'Manual', 'true')
        else: addvalue(x_temp, 'Manual', 'false')
    else:
        addvalue(x_temp, 'Manual', param_value)
    if auto_id != None: add_env_target(x_temp, 'AutomationTarget', auto_id)
    if modu_id != None: add_env_target(x_temp, 'ModulationTarget', modu_id)
    if midi_cont_range != None: add_min_max(x_temp, 'MidiControllerRange', midi_cont_range[0], midi_cont_range[1], False)
    if midi_cc_thres != None: add_min_max(x_temp, 'MidiCCOnOffThresholds', midi_cc_thres[0], midi_cc_thres[1], True)
      
def set_add_param_nosub(param_name, param_value, auto_id, modu_id, midi_cc_thres, midi_cont_range):
    x_temp = ET.Element(param_name)
    addvalue(x_temp, 'LomId', '0')
    if isinstance(param_value, bool): 
        if param_value: addvalue(x_temp, 'Manual', 'true')
        else: addvalue(x_temp, 'Manual', 'false')
    else:
        addvalue(x_temp, 'Manual', param_value)
    if auto_id != None: add_env_target(x_temp, 'AutomationTarget', auto_id)
    if modu_id != None: add_env_target(x_temp, 'ModulationTarget', modu_id)
    if midi_cont_range != None: add_min_max(x_temp, 'MidiControllerRange', midi_cont_range[0], midi_cont_range[1], False)
    if midi_cc_thres != None: add_min_max(x_temp, 'MidiCCOnOffThresholds', midi_cc_thres[0], midi_cc_thres[1], True)
    return x_temp

def create_devicechain_mixer(xmltag, cvpj_track_data, tracktype):
    global cvpj_bpm
    global master_returnid
    xmltag = ET.SubElement(xmltag, 'Mixer')
    addvalue(xmltag, 'LomId', '0')
    addvalue(xmltag, 'LomIdView', '0')
    addvalue(xmltag, 'IsExpanded', 'true')
    set_add_param(xmltag, 'On', 'true', str(counter_unused_id.get()), None, [64,127], None)
    addvalue(xmltag, 'ModulationSourceCount', '0')
    addLomId(xmltag, 'ParametersListWrapper', '0')
    addId(xmltag, 'Pointee', str(counter_pointee.get()))
    addvalue(xmltag, 'LastSelectedTimeableIndex', '0')
    addvalue(xmltag, 'LastSelectedClipEnvelopeIndex', '0')
    x_LastPresetRef = ET.SubElement(xmltag, 'LastPresetRef')
    x_LastPresetRef_Value = ET.SubElement(x_LastPresetRef, 'Value')
    x_LockedScripts = ET.SubElement(xmltag, 'LockedScripts')
    addvalue(xmltag, 'IsFolded', 'false')
    addvalue(xmltag, 'ShouldShowPresetName', 'false')
    addvalue(xmltag, 'UserName', '')
    addvalue(xmltag, 'Annotation', '')
    x_SourceContext = ET.SubElement(xmltag, 'SourceContext')
    x_SourceContext_Value = ET.SubElement(x_SourceContext, 'Value')
    x_Sends = ET.SubElement(xmltag, 'Sends')

    trk_vol = params.get(cvpj_track_data, [], 'vol', 1)[0]
    trk_pan = params.get(cvpj_track_data, [], 'pan', 0)[0]

    cvpj_track_sends = {}
    if 'sends_audio' in cvpj_track_data:
        for cvpj_track_data_send in cvpj_track_data['sends_audio']:
            cvpj_track_sends[master_returnid[cvpj_track_data_send['sendid']]] = cvpj_track_data_send['amount']

    if tracktype not in ['master', 'prehear']:
        for master_returnid_s in master_returnid:
            sendamount = 0
            if master_returnid[master_returnid_s] in cvpj_track_sends: sendamount = cvpj_track_sends[master_returnid[master_returnid_s]]
            x_TrackSendHolder = ET.SubElement(x_Sends, "TrackSendHolder")
            x_TrackSendHolder.set('Id', str(master_returnid[master_returnid_s]))
            set_add_param(x_TrackSendHolder, 'Send', str(sendamount), str(counter_unused_id.get()), counter_unused_id.get(), None, [0.0003162277571,1])
            if tracktype in ['miditrack', 'audiotrack']: addvalue(x_TrackSendHolder, 'Active', 'true')
            else: addvalue(x_TrackSendHolder, 'Active', 'false')

    set_add_param(xmltag, 'Speaker', 'true', str(counter_unused_id.get()), None, [64,127], None)
    addvalue(xmltag, 'SoloSink', 'false')
    addvalue(xmltag, 'PanMode', '0')
    set_add_param(xmltag, 'Pan', trk_pan, str(counter_unused_id.get()), str(counter_unused_id.get()), None, [-1,1])
    set_add_param(xmltag, 'SplitStereoPanL', '-1', str(counter_unused_id.get()), str(counter_unused_id.get()), None, [-1,1])
    set_add_param(xmltag, 'SplitStereoPanR', '1', str(counter_unused_id.get()), str(counter_unused_id.get()), None, [-1,1])
    set_add_param(xmltag, 'Volume', trk_vol, str(counter_unused_id.get()), str(counter_unused_id.get()), None, [0.0003162277571,1.99526238])
    addvalue(xmltag, 'ViewStateSesstionTrackWidth', '93')
    set_add_param(xmltag, 'CrossFadeState', '1', str(counter_unused_id.get()), None, None, None)
    addLomId(xmltag, 'SendsListWrapper', '0')
    if tracktype == 'master':
        set_add_param(xmltag, 'Tempo', str(cvpj_bpm), str(counter_unused_id.get()), str(counter_unused_id.get()), None, [60,200])
        set_add_param(xmltag, 'TimeSignature', '201', str(counter_unused_id.get()), None, None, None)
        set_add_param(xmltag, 'GlobalGrooveAmount', '100', str(counter_unused_id.get()), str(counter_unused_id.get()), None, [0,131.25])
        set_add_param(xmltag, 'CrossFade', '0', str(counter_unused_id.get()), str(counter_unused_id.get()), None, [-1,1])
        addvalue(xmltag, 'TempoAutomationViewBottom', '60')
        addvalue(xmltag, 'TempoAutomationViewTop', '200')

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

# ---------------- Track Base / MainSequencer / MIDI Clips ----------------

def make_auto_point(xmltag, value, position, SubElementname):
    x_autopoint = ET.SubElement(xmltag, SubElementname)
    x_autopoint.set('TimeOffset', str(position/4))
    x_autopoint.set('Value', str(value))
    x_autopoint.set('CurveControl1X', '0.5')
    x_autopoint.set('CurveControl1Y', '0.5')
    x_autopoint.set('CurveControl2X', '0.5')
    x_autopoint.set('CurveControl2Y', '0.5')

def t_parse_automation(xmltag, cvpj_points):
    cvpj_points_no_instant = auto.remove_instant_note(cvpj_points)
    for cvpj_point in cvpj_points_no_instant:
        make_auto_point(xmltag, cvpj_point['value']*170, cvpj_point['position'], "PerNoteEvent")

def create_notelist(xmltag, cvpj_notelist):
    t_keydata = {}
    x_KeyTracks = ET.SubElement(xmltag, 'KeyTracks')
    for note in cvpj_notelist:
        if note['key'] not in t_keydata: t_keydata[note['key']] = []
        note['id'] = counter_note.get()
        t_keydata[note['key']].append(note)

    t_keydata = dict(sorted(t_keydata.items(), key=lambda item: item[0]))

    t_notemod = {}

    for keynum in t_keydata:
        x_KeyTrack = addId(x_KeyTracks, 'KeyTrack', str(counter_keytrack.get()))
        x_KeyTrack_notes = ET.SubElement(x_KeyTrack, 'Notes')
        for t_note in t_keydata[keynum]:
            x_MidiNoteEvent = ET.SubElement(x_KeyTrack_notes, 'MidiNoteEvent')
            x_MidiNoteEvent.set('Time', str(t_note['position']/4))
            x_MidiNoteEvent.set('Duration', str(t_note['duration']/4))
            if 'vol' in t_note: x_MidiNoteEvent.set('Velocity', str(t_note['vol']*100))
            else: x_MidiNoteEvent.set('Velocity', "100")
            x_MidiNoteEvent.set('VelocityDeviation', "0")
            if 'off_vol' in t_note: x_MidiNoteEvent.set('OffVelocity', str(t_note['off_vol']*100))
            else: x_MidiNoteEvent.set('OffVelocity', "64")
            if 'probability' in t_note: x_MidiNoteEvent.set('Probability', str(t_note['probability']))
            else: x_MidiNoteEvent.set('Probability', "1")
            if 'enabled' in t_note:
                if t_note['enabled'] == 1: x_MidiNoteEvent.set('IsEnabled', "true")
                if t_note['enabled'] == 0: x_MidiNoteEvent.set('IsEnabled', "false")
            else: x_MidiNoteEvent.set('IsEnabled', "true")
            if 'notemod' in t_note:
                if 'auto' in t_note['notemod']:
                    t_notemod[t_note['id']] = t_note['notemod']['auto']
            x_MidiNoteEvent.set('NoteId', str(t_note['id']))
        addvalue(x_KeyTrack, 'MidiKey', str(keynum+60))

    x_PerNoteEventStore = ET.SubElement(xmltag, 'PerNoteEventStore')
    x_EventLists = ET.SubElement(x_PerNoteEventStore, 'EventLists')

    PerNoteEventListID = 0
    for notemodnum in t_notemod:
        x_PerNoteEventList = ET.SubElement(x_EventLists, "PerNoteEventList")
        x_PerNoteEventList.set('Id', str(PerNoteEventListID))
        x_PerNoteEventList.set('NoteId', str(notemodnum))
        x_PerNoteEventList.set('CC', "-2")
        x_PerNoteEvents = ET.SubElement(x_PerNoteEventList, "Events")
        if 'pitch' in t_notemod[notemodnum]:
            t_parse_automation(x_PerNoteEvents, t_notemod[notemodnum]['pitch'])
        PerNoteEventListID += 1

    x_NoteIdGenerator = ET.SubElement(xmltag, 'NoteIdGenerator')
    addvalue(x_NoteIdGenerator, 'NextId', str(counter_note.next()+1))

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

# ---------------- Track Base / MainSequencer / Audio Clips ----------------

def create_sampleref(xmltag, aud_sampledata, idnum):
    x_SampleRef = ET.SubElement(xmltag, 'SampleRef')
    if idnum != None: x_SampleRef.set('Id', str(idnum))
    x_FileRef = ET.SubElement(x_SampleRef, 'FileRef')
    addvalue(x_FileRef, 'RelativePathType', '1')
    addvalue(x_FileRef, 'RelativePath', '')
    addvalue(x_FileRef, 'Path', aud_sampledata['path'])
    addvalue(x_FileRef, 'Type', '1')
    addvalue(x_FileRef, 'LivePackName', '')
    addvalue(x_FileRef, 'LivePackId', '')
    addvalue(x_FileRef, 'OriginalFileSize', aud_sampledata['file_size'])
    addvalue(x_FileRef, 'OriginalCrc', aud_sampledata['crc'])
    addvalue(x_SampleRef, 'LastModDate', aud_sampledata['mod_date'])
    x_SourceContext = ET.SubElement(x_SampleRef, 'SourceContext')
    addvalue(x_SampleRef, 'SampleUsageHint', '0')
    addvalue(x_SampleRef, 'DefaultDuration', aud_sampledata['dur'])
    addvalue(x_SampleRef, 'DefaultSampleRate', aud_sampledata['rate'])

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

def create_clip(xmltag, cliptype, cvpj_placement, trackcolor):
    cvpj_position = cvpj_placement['position']
    cvpj_duration = cvpj_placement['duration']

    able_position = cvpj_position/4
    able_duration = cvpj_duration/4

    t_name = ''
    t_color = trackcolor
    t_notelist = []
    t_disabled = 'false'
    if 'name' in cvpj_placement: t_name = cvpj_placement['name']
    if 'color' in cvpj_placement: t_color = colors.closest_color_index(colorlist_one, cvpj_placement['color'])
    if 'notelist' in cvpj_placement: t_notelist = notelist_data.sort(cvpj_placement['notelist'])
    if 'muted' in cvpj_placement: 
        if cvpj_placement['muted'] == 1: 
            t_disabled = 'true'

    # ------------------------------------------ audio ------------------------------------------
    t_file = ''
    t_vol = 1

    tempomul = (cvpj_bpm/120)

    if cliptype == 'audio':
        if 'file' in cvpj_placement: t_file = cvpj_placement['file']
        aud_sampledata = audio.get_audiofile_info(t_file)
        AudioDuration = aud_sampledata['dur_sec']
        normalspeed = (AudioDuration)*tempomul
        w_timemarkers = [{'pos': 0.0, 'pos_real': 0.0},{'pos': normalspeed, 'pos_real': AudioDuration/8}]
        if 'vol' in cvpj_placement: t_vol = cvpj_placement['vol']

    w_IsWarped = 'false'
    w_WarpMode = 4
    w_ComplexProEnvelope = 128
    w_ComplexProFormants = 100
    w_FluctuationTexture = 25
    w_GranularityTexture = 65
    w_GranularityTones = 30
    w_TransientEnvelope = 100 
    w_TransientLoopMode = 2
    w_TransientResolution = 6
    stretch_t_steps = able_duration
    stretch_t_pitch = 0
    FadeEnabled = 'false'
    FadeInCurveSkew = 0
    FadeInCurveSlope = 0
    FadeInLength = 0
    FadeOutCurveSkew = 0
    FadeOutCurveSlope = 0
    FadeOutLength = 0
    t_CurrentStart = able_position
    t_CurrentEnd = able_duration+able_position
    t_LoopStart = 0
    t_StartRelative = 0
    t_LoopOn = 'false'
    cvpj_stretchmode = 'none'
    cvpj_isstretched = False
    cvpj_islooped = False

    if cliptype == 'audio':
        t_LoopEnd = None

        if 'cut' in cvpj_placement:
            cvpj_placement_cut = cvpj_placement['cut']

        if 'audiomod' in cvpj_placement:
            cvpj_audiomod = cvpj_placement['audiomod']

            if 'pitch' in cvpj_audiomod: stretch_t_pitch = cvpj_audiomod['pitch']
            if 'stretch_method' in cvpj_audiomod: 
                if cvpj_audiomod['stretch_method'] == 'warp': w_IsWarped = 'true'

            if w_IsWarped == 'true':
                if 'stretch_params' in cvpj_audiomod: 
                    stretch_params = cvpj_audiomod['stretch_params']
                    if 'ComplexProEnvelope' in stretch_params: w_ComplexProEnvelope = stretch_params['ComplexProEnvelope']
                    if 'ComplexProFormants' in stretch_params: w_ComplexProFormants = stretch_params['ComplexProFormants']
                    if 'FluctuationTexture' in stretch_params: w_FluctuationTexture = stretch_params['FluctuationTexture']
                    if 'GranularityTexture' in stretch_params: w_GranularityTexture = stretch_params['GranularityTexture']
                    if 'GranularityTones' in stretch_params: w_GranularityTones = stretch_params['GranularityTones']
                    if 'TransientEnvelope' in stretch_params: w_TransientEnvelope = stretch_params['TransientEnvelope']
                    if 'TransientLoopMode' in stretch_params: w_TransientLoopMode = stretch_params['TransientLoopMode']
                    if 'TransientResolution' in stretch_params: w_TransientResolution = stretch_params['TransientResolution']

                if 'stretch_algorithm' in cvpj_audiomod: 
                    if cvpj_audiomod['stretch_algorithm'] == 'beats': w_WarpMode = 0
                    if cvpj_audiomod['stretch_algorithm'] == 'ableton_tones': w_WarpMode = 1
                    if cvpj_audiomod['stretch_algorithm'] == 'ableton_texture': w_WarpMode = 2
                    if cvpj_audiomod['stretch_algorithm'] == 'resample': w_WarpMode = 3
                    if cvpj_audiomod['stretch_algorithm'] == 'ableton_complex': w_WarpMode = 4
                    if cvpj_audiomod['stretch_algorithm'] == 'stretch_complexpro': w_WarpMode = 6

                if 'stretch_data' in cvpj_audiomod: 
                    if cvpj_audiomod['stretch_data'] != []: w_timemarkers = cvpj_audiomod['stretch_data']

        if 'cut' in cvpj_placement:
            cvpj_placement_cut = cvpj_placement['cut']
            if 'type' in cvpj_placement_cut:
                if w_IsWarped == 'true':
                    if cvpj_placement_cut['type'] == 'cut':
                        if 'start' in cvpj_placement_cut: t_LoopStart = cvpj_placement_cut['start']/4
                        if 'end' in cvpj_placement_cut: t_LoopEnd = cvpj_placement_cut['end']/4
                    if cvpj_placement_cut['type'] in ['loop', 'loop_off', 'loop_adv']:
                        t_LoopOn = 'true'
                        t_StartRelative = cvpj_placement_cut['start']/4 if 'start' in cvpj_placement_cut else 0
                        t_LoopStart = cvpj_placement_cut['loopstart']/4 if 'loopstart' in cvpj_placement_cut else 0
                        t_LoopEnd = cvpj_placement_cut['loopend']/4

                else:
                    if cvpj_placement_cut['type'] == 'cut':
                        if 'start' in cvpj_placement_cut: t_LoopStart = cvpj_placement_cut['start']
                        if 'end' in cvpj_placement_cut: t_LoopEnd = cvpj_placement_cut['end']

        timemarkerdur = (w_timemarkers[-1]['pos_real']-w_timemarkers[0]['pos_real'])
        ifnotexist = ((AudioDuration/timemarkerdur)*AudioDuration)*2

        #print('---------------------------------------- ',AudioDuration, timemarkerdur, ifnotexist)

        if t_LoopEnd == None: t_LoopEnd = ifnotexist


    else:
        t_CurrentStart = able_position
        t_LoopEnd = (able_duration+able_position)

        if 'cut' in cvpj_placement:
            cvpj_placement_cut = cvpj_placement['cut']
            if 'type' in cvpj_placement_cut:

                if cvpj_placement_cut['type'] == 'cut':
                    t_LoopOn = 'false'
                    if 'start' in cvpj_placement_cut: 
                        t_LoopStart = (cvpj_placement_cut['start']/4)
                        t_LoopEnd = able_duration+t_LoopStart
                    t_StartRelative = 0

                if cvpj_placement_cut['type'] in ['loop', 'loop_off', 'loop_adv']:
                    t_LoopOn = 'true'
                    t_StartRelative = cvpj_placement_cut['start']/4 if 'start' in cvpj_placement_cut else 0
                    t_LoopStart = cvpj_placement_cut['loopstart']/4 if 'loopstart' in cvpj_placement_cut else 0
                    t_LoopEnd = cvpj_placement_cut['loopend']/4
        else:
            t_LoopStart = 0
            t_LoopEnd = able_duration

    if cliptype == 'notes': x_ClipData = addId(xmltag, 'MidiClip', str(counter_clip.get()))
    if cliptype == 'audio': x_ClipData = addId(xmltag, 'AudioClip', str(counter_clip.get()))
    x_ClipData.set('Time', str(able_position))

    addvalue(x_ClipData, 'LomId', '0')
    addvalue(x_ClipData, 'LomIdView', '0')

    addvalue(x_ClipData, 'CurrentStart', str(t_CurrentStart))
    addvalue(x_ClipData, 'CurrentEnd', str(t_CurrentEnd))
    x_ClipData_loop = ET.SubElement(x_ClipData, 'Loop')
    addvalue(x_ClipData_loop, 'LoopStart', str(t_LoopStart))
    addvalue(x_ClipData_loop, 'LoopEnd', str(t_LoopEnd))
    addvalue(x_ClipData_loop, 'StartRelative', str(t_StartRelative))
    addvalue(x_ClipData_loop, 'LoopOn', t_LoopOn)
    addvalue(x_ClipData_loop, 'OutMarker', t_LoopEnd)
    addvalue(x_ClipData_loop, 'HiddenLoopStart', t_LoopStart)
    addvalue(x_ClipData_loop, 'HiddenLoopEnd', t_LoopEnd)

    #for value in [t_CurrentStart, t_CurrentEnd, t_StartRelative, t_LoopStart, t_LoopEnd]:
    #    print(str(value).ljust(20), end=' ')
    #print()

    addvalue(x_ClipData, 'Name', t_name)
    addvalue(x_ClipData, 'Annotation', '')
    addvalue(x_ClipData, 'Color', str(t_color))
    addvalue(x_ClipData, 'LaunchMode', "0")
    addvalue(x_ClipData, 'LaunchQuantisation', "0")
    x_ClipData_TimeSignature = ET.SubElement(x_ClipData, 'TimeSignature')
    x_ClipData_TimeSignature_s = ET.SubElement(x_ClipData_TimeSignature, 'TimeSignatures')
    x_ClipData_TimeSignature_s_remote = addId(x_ClipData_TimeSignature_s, 'RemoteableTimeSignature', '0')
    addvalue(x_ClipData_TimeSignature_s_remote, 'Numerator', '4')
    addvalue(x_ClipData_TimeSignature_s_remote, 'Denominator', '4')
    addvalue(x_ClipData_TimeSignature_s_remote, 'Time', '0')

    x_ClipData_Envelopes = ET.SubElement(x_ClipData, 'Envelopes')
    ET.SubElement(x_ClipData_Envelopes, 'Envelopes')
    x_ClipData_ScrollerTimePreserver = ET.SubElement(x_ClipData, 'ScrollerTimePreserver')
    addvalue(x_ClipData_ScrollerTimePreserver, 'LeftTime', t_CurrentStart)
    addvalue(x_ClipData_ScrollerTimePreserver, 'RightTime', t_CurrentEnd)

    # ------------------------------------------ audio ------------------------------------------
    if cliptype == 'audio':
        x_ClipData_TimeSelection = ET.SubElement(x_ClipData, 'TimeSelection')
        addvalue(x_ClipData_TimeSelection, 'AnchorTime', '0')
        addvalue(x_ClipData_TimeSelection, 'OtherTime', '0')
    # -------------------------------------------------------------------------------------------

    addvalue(x_ClipData, 'Legato', 'false')
    addvalue(x_ClipData, 'Ram', 'false')
    x_ClipData_GrooveSettings = ET.SubElement(x_ClipData, 'GrooveSettings')
    addvalue(x_ClipData_GrooveSettings, 'GrooveId', '-1')
    addvalue(x_ClipData, 'Disabled', t_disabled)
    addvalue(x_ClipData, 'VelocityAmount', '0')
    create_FollowAction(x_ClipData, 4, 'true', 1, [4,0], [100,0], [1,1], 'false')
    create_grid(x_ClipData, 'Grid', 1, 16, 20, 2, 'true', 'true')
    addvalue(x_ClipData, 'FreezeStart', '0')
    addvalue(x_ClipData, 'FreezeEnd', '0')

    if cliptype == 'notes':
        addvalue(x_ClipData, 'IsWarped', 'true')
        addvalue(x_ClipData, 'TakeId', '1')
        x_ClipDataNotes = ET.SubElement(x_ClipData, 'Notes')
        create_notelist(x_ClipDataNotes, t_notelist)
        addvalue(x_ClipData, 'BankSelectCoarse', '-1')
        addvalue(x_ClipData, 'BankSelectFine', '-1')
        addvalue(x_ClipData, 'ProgramChange', '-1')
        create_scaleinformation(x_ClipData)
        addvalue(x_ClipData, 'IsInKey', 'false')
        addvalue(x_ClipData, 'NoteSpellingPreference', '3')
        addvalue(x_ClipData, 'PreferFlatRootNote', 'false')
        create_grid(x_ClipData, 'ExpressionGrid', 1, 16, 20, 2, 'false', 'false')

    if cliptype == 'audio':
        t_pitch = stretch_t_pitch
        w_PitchCoarse = round(t_pitch)
        w_PitchFine = (t_pitch-round(t_pitch))*100

        addvalue(x_ClipData, 'IsWarped', w_IsWarped)
        addvalue(x_ClipData, 'TakeId', '1')
        create_sampleref(x_ClipData, aud_sampledata, None)
        x_ClipData_Onsets = ET.SubElement(x_ClipData, 'Onsets')
        x_ClipData_UserOnsets = ET.SubElement(x_ClipData_Onsets, 'UserOnsets')
        addvalue(x_ClipData_Onsets, 'HasUserOnsets', 'false')
        addvalue(x_ClipData, 'WarpMode', w_WarpMode)
        addvalue(x_ClipData, 'GranularityTones', w_GranularityTones)
        addvalue(x_ClipData, 'GranularityTexture', w_GranularityTexture)
        addvalue(x_ClipData, 'FluctuationTexture', w_FluctuationTexture)
        addvalue(x_ClipData, 'TransientResolution', w_TransientResolution)
        addvalue(x_ClipData, 'TransientLoopMode', w_TransientLoopMode)
        addvalue(x_ClipData, 'TransientEnvelope', w_TransientEnvelope)
        addvalue(x_ClipData, 'ComplexProFormants', w_ComplexProFormants)
        addvalue(x_ClipData, 'ComplexProEnvelope', w_ComplexProEnvelope)

        addvalue(x_ClipData, 'Sync', 'true')
        addvalue(x_ClipData, 'HiQ', 'true')

        if 'fade' in cvpj_placement:
            FadeEnabled = 'true'
            cvpj_fade = cvpj_placement['fade']
            if 'in' in cvpj_fade:
                if 'duration' in cvpj_fade['in']: FadeInLength = cvpj_fade['in']['duration']/8
                if 'skew' in cvpj_fade['in']: FadeInCurveSkew = cvpj_fade['in']['skew']
                if 'slope' in cvpj_fade['in']: FadeInCurveSlope = cvpj_fade['in']['slope']
            if 'out' in cvpj_fade:
                if 'duration' in cvpj_fade['out']: FadeOutLength = cvpj_fade['out']['duration']/8
                if 'skew' in cvpj_fade['out']: FadeOutCurveSkew = cvpj_fade['out']['skew']
                if 'slope' in cvpj_fade['out']: FadeOutCurveSlope = cvpj_fade['out']['slope']

        addvalue(x_ClipData, 'Fade', FadeEnabled)
        x_ClipData_Fades = ET.SubElement(x_ClipData, 'Fades')
        addvalue(x_ClipData_Fades, 'FadeInLength', FadeInLength*8)
        addvalue(x_ClipData_Fades, 'FadeOutLength', FadeOutLength*8)
        addvalue(x_ClipData_Fades, 'ClipFadesAreInitialized', 'true')
        addvalue(x_ClipData_Fades, 'CrossfadeInState', '0')
        addvalue(x_ClipData_Fades, 'FadeInCurveSkew', FadeInCurveSkew)
        addvalue(x_ClipData_Fades, 'FadeInCurveSlope', FadeInCurveSlope)
        addvalue(x_ClipData_Fades, 'FadeOutCurveSkew', FadeOutCurveSkew)
        addvalue(x_ClipData_Fades, 'FadeOutCurveSlope', FadeOutCurveSlope)
        addvalue(x_ClipData_Fades, 'IsDefaultFadeIn', 'false') 
        addvalue(x_ClipData_Fades, 'IsDefaultFadeOut', 'false')

        addvalue(x_ClipData, 'PitchCoarse', w_PitchCoarse)
        addvalue(x_ClipData, 'PitchFine', w_PitchFine)
        addvalue(x_ClipData, 'SampleVolume', t_vol)
        addvalue(x_ClipData, 'MarkerDensity', '2')
        addvalue(x_ClipData, 'AutoWarpTolerance', '4')

        x_ClipData_WarpMarkers = ET.SubElement(x_ClipData, 'WarpMarkers')

        warpid = 0
        for w_timemarker in w_timemarkers:
            x_ClipData_WarpMarker = ET.SubElement(x_ClipData_WarpMarkers, 'WarpMarker')
            x_ClipData_WarpMarker.set('Id', str(warpid))
            x_ClipData_WarpMarker.set('SecTime', str(w_timemarker['pos_real']))
            x_ClipData_WarpMarker.set('BeatTime', str(w_timemarker['pos']/4))
            warpid += 1

        x_ClipData_SavedWarpMarkersForStretched = ET.SubElement(x_ClipData, 'SavedWarpMarkersForStretched')
        addvalue(x_ClipData, 'MarkersGenerated', 'true')
        addvalue(x_ClipData, 'IsSongTempoMaster', 'false')

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------

# ---------------- Track Base / MainSequencer ----------------

def set_add_clipslots(x_MainSequencer):
    x_ClipSlotList = ET.SubElement(x_MainSequencer, 'ClipSlotList')
    for clipslotnum in range(8):
        x_ClipSlot = addId(x_ClipSlotList, 'ClipSlot', str(clipslotnum))
        addvalue(x_ClipSlot, 'LomId', '0')
        x_ClipSlot_i = ET.SubElement(x_ClipSlot, 'ClipSlot')
        ET.SubElement(x_ClipSlot_i, 'Value')
        addvalue(x_ClipSlot, 'HasStop', 'true')
        addvalue(x_ClipSlot, 'NeedRefreeze', 'true')
    return x_ClipSlotList

def set_add_sequencer_base(x_BaseSequencer):
    addvalue(x_BaseSequencer, 'LomId', '0')
    addvalue(x_BaseSequencer, 'LomIdView', '0')
    addvalue(x_BaseSequencer, 'IsExpanded', 'true')
    set_add_param(x_BaseSequencer, 'On', 'true', str(counter_unused_id.get()), None, [64,127], None)
    addvalue(x_BaseSequencer, 'ModulationSourceCount', '0')
    addLomId(x_BaseSequencer, 'ParametersListWrapper', '0')
    addId(x_BaseSequencer, 'Pointee', str(counter_pointee.get()))
    addvalue(x_BaseSequencer, 'LastSelectedTimeableIndex', '0')
    addvalue(x_BaseSequencer, 'LastSelectedClipEnvelopeIndex', '0')
    x_LastPresetRef = ET.SubElement(x_BaseSequencer, 'LastPresetRef')
    ET.SubElement(x_LastPresetRef, 'Value')
    x_LockedScripts = ET.SubElement(x_BaseSequencer, 'LockedScripts')
    addvalue(x_BaseSequencer, 'IsFolded', 'false')
    addvalue(x_BaseSequencer, 'ShouldShowPresetName', 'true')
    addvalue(x_BaseSequencer, 'UserName', '')
    addvalue(x_BaseSequencer, 'Annotation', '')
    x_SourceContext = ET.SubElement(x_BaseSequencer, 'SourceContext')
    ET.SubElement(x_SourceContext, 'Value')
    #addvalue(x_ClipSlotList, 'MonitoringEnum', '1')

def set_add_midi_track_freezesequencer(xmltag, track_placements):
    x_FreezeSequencer = ET.SubElement(xmltag, 'FreezeSequencer')
    set_add_sequencer_base(x_FreezeSequencer)
    x_ClipSlotList = set_add_clipslots(x_FreezeSequencer)
    set_add_sequencer_end(xmltag)

def set_add_sequencer_end(x_FreezeSequencer):
    add_env_target(x_FreezeSequencer, 'VolumeModulationTarget', counter_unused_id.get())
    add_env_target(x_FreezeSequencer, 'TranspositionModulationTarget', counter_unused_id.get())
    add_env_target(x_FreezeSequencer, 'GrainSizeModulationTarget', counter_unused_id.get())
    add_env_target(x_FreezeSequencer, 'FluxModulationTarget', counter_unused_id.get())
    add_env_target(x_FreezeSequencer, 'SampleOffsetModulationTarget', counter_unused_id.get())
    addvalue(x_FreezeSequencer, 'PitchViewScrollPosition', '-1073741824')
    addvalue(x_FreezeSequencer, 'SampleOffsetModulationScrollPosition', '-1073741824')
    x_Recorder = ET.SubElement(x_FreezeSequencer, 'Recorder')
    addvalue(x_Recorder, 'IsArmed', 'false')
    addvalue(x_Recorder, 'TakeCounter', '0')

# ---------------- Track Base / Device Chain ----------------

def create_devicechain(xmltag, cvpj_track_data, tracktype, track_placements, trackcolor):
    global LaneHeight
    # ------- AutomationLanes
    x_AutomationLanes = ET.SubElement(xmltag, 'AutomationLanes')
    x_AutomationLanes_i = ET.SubElement(x_AutomationLanes, 'AutomationLanes')
    x_AutomationTarget = addId(x_AutomationLanes_i, 'AutomationLane', '0')
    addvalue(x_AutomationTarget, 'SelectedDevice', '0')
    addvalue(x_AutomationTarget, 'SelectedEnvelope', '0')
    addvalue(x_AutomationTarget, 'IsContentSelectedInDocument', 'false')
    addvalue(x_AutomationTarget, 'LaneHeight', str(LaneHeight))
    addvalue(x_AutomationLanes, 'AreAdditionalAutomationLanesFolded', 'false')

    x_ClipEnvelopeChooserViewState = ET.SubElement(xmltag, 'ClipEnvelopeChooserViewState')
    addvalue(x_ClipEnvelopeChooserViewState, 'SelectedDevice', '0')
    addvalue(x_ClipEnvelopeChooserViewState, 'SelectedEnvelope', '0')
    addvalue(x_ClipEnvelopeChooserViewState, 'PreferModulationVisible', 'false')

    add_up_lower(xmltag, 'AudioInputRouting', 'AudioIn/External/S0', 'Ext. In', '1/2')
    add_up_lower(xmltag, 'MidiInputRouting', 'MidiIn/External.All/-1', 'Ext: All Ins', '')
    if tracktype == 'miditrack': add_up_lower(xmltag, 'AudioOutputRouting', 'AudioOut/Master', 'Master', '')
    elif tracktype == 'audiotrack': add_up_lower(xmltag, 'AudioOutputRouting', 'AudioOut/Master', 'Master', '')
    elif tracktype == 'returntrack': add_up_lower(xmltag, 'AudioOutputRouting', 'AudioOut/Master', 'Master', '')
    elif tracktype == 'master': add_up_lower(xmltag, 'AudioOutputRouting', 'AudioOut/External/S0', 'Ext. Out', '1/2')
    elif tracktype == 'prehear': add_up_lower(xmltag, 'AudioOutputRouting', 'AudioOut/External/S0', 'Ext. Out', '')

    add_up_lower(xmltag, 'MidiOutputRouting', 'MidiOut/None', 'None', '')
    create_devicechain_mixer(xmltag, cvpj_track_data, tracktype)

    x_DeviceChain_i = ET.SubElement(xmltag, 'DeviceChain')
    x_DeviceChain_i_Devices = ET.SubElement(x_DeviceChain_i, 'Devices')

    middlenote = data_values.nested_dict_get_value(cvpj_track_data, ['instdata', 'middlenote'])
    if middlenote == None: middlenote = 0

    if tracktype == 'miditrack':
        #mainsequencer
        x_MainSequencer = ET.SubElement(xmltag, 'MainSequencer')
        set_add_sequencer_base(x_MainSequencer)
        x_ClipSlotList = set_add_clipslots(x_MainSequencer)
        x_ClipTimeable = ET.SubElement(x_MainSequencer, 'ClipTimeable')
        x_ArrangerAutomation = ET.SubElement(x_ClipTimeable, 'ArrangerAutomation')
        x_ArrangerAutomation_Events = ET.SubElement(x_ArrangerAutomation, 'Events')
        for cvpj_placement in track_placements:
            create_clip(x_ArrangerAutomation_Events, 'notes', cvpj_placement, trackcolor)
        create_timeselection(xmltag, 0, 4)
        x_ArrangerAutomation_AutomationTransformViewState = ET.SubElement(x_ArrangerAutomation, 'AutomationTransformViewState')
        addvalue(x_ArrangerAutomation_AutomationTransformViewState, 'IsTransformPending', 'false')
        ET.SubElement(x_ArrangerAutomation_AutomationTransformViewState, 'TimeAndValueTransforms')
        x_Recorder = ET.SubElement(x_MainSequencer, 'Recorder')
        addvalue(x_Recorder, 'IsArmed', 'false')
        addvalue(x_Recorder, 'TakeCounter', '0')
        x_MidiControllers = ET.SubElement(x_MainSequencer, 'MidiControllers')
        for clipslotnum in range(131):
            add_env_target(x_MidiControllers, 'ControllerTargets.'+str(clipslotnum), counter_cont.get())
        #freezesequencer
        x_FreezeSequencer = ET.SubElement(xmltag, 'FreezeSequencer')
        set_add_sequencer_base(x_FreezeSequencer)
        x_ClipSlotList = set_add_clipslots(x_FreezeSequencer)
        set_add_sequencer_end(x_FreezeSequencer)

        if middlenote != 0:
            xml_pitch = do_device_data_intro(x_DeviceChain_i_Devices, 4, 'MidiPitcher', True, '')
            set_add_param(xml_pitch, 'Pitch', -middlenote, None, None, [-128, 128], None)


    if tracktype == 'audiotrack':
        #mainsequencer
        x_MainSequencer = ET.SubElement(xmltag, 'MainSequencer')
        set_add_sequencer_base(x_MainSequencer)
        x_ClipSlotList = set_add_clipslots(x_MainSequencer)
        addvalue(x_MainSequencer, 'MonitoringEnum', '2')
        x_Sample = ET.SubElement(x_MainSequencer, 'Sample')
        x_ArrangerAutomation = ET.SubElement(x_Sample, 'ArrangerAutomation')
        x_ArrangerAutomation_Events = ET.SubElement(x_ArrangerAutomation, 'Events')
        for track_placement in track_placements:
            create_clip(x_ArrangerAutomation_Events, 'audio', track_placement, trackcolor)
        x_ArrangerAutomation_AutomationTransformViewState = ET.SubElement(x_ArrangerAutomation, 'AutomationTransformViewState')
        addvalue(x_ArrangerAutomation_AutomationTransformViewState, 'IsTransformPending', 'false')
        ET.SubElement(x_ArrangerAutomation_AutomationTransformViewState, 'TimeAndValueTransforms')
        set_add_sequencer_end(x_MainSequencer)
        #freezesequencer
        x_FreezeSequencer = ET.SubElement(xmltag, 'FreezeSequencer')
        set_add_sequencer_base(x_FreezeSequencer)
        x_ClipSlotList = set_add_clipslots(x_FreezeSequencer)
        addvalue(x_FreezeSequencer, 'MonitoringEnum', '2')
        x_Sample = ET.SubElement(x_FreezeSequencer, 'Sample')
        x_ArrangerAutomation = ET.SubElement(x_Sample, 'ArrangerAutomation')
        x_ArrangerAutomation_Events = ET.SubElement(x_ArrangerAutomation, 'Events')
        x_ArrangerAutomation_AutomationTransformViewState = ET.SubElement(x_ArrangerAutomation, 'AutomationTransformViewState')
        addvalue(x_ArrangerAutomation_AutomationTransformViewState, 'IsTransformPending', 'false')
        ET.SubElement(x_ArrangerAutomation_AutomationTransformViewState, 'TimeAndValueTransforms')
        set_add_sequencer_end(x_FreezeSequencer)

    if tracktype == 'master':
        x_FreezeSequencer = ET.SubElement(xmltag, 'FreezeSequencer')
        x_AudioSequencer = addId(x_FreezeSequencer, 'AudioSequencer', '0')
        set_add_sequencer_base(x_AudioSequencer)
        ET.SubElement(xmltag, 'ClipSlotList')

        ET.SubElement(x_AudioSequencer, 'ClipSlotList')
        addvalue(x_AudioSequencer, 'MonitoringEnum', '1')
        x_Sample = ET.SubElement(x_AudioSequencer, 'Sample')
        x_ArrangerAutomation = ET.SubElement(x_Sample, 'ArrangerAutomation')
        x_ArrangerAutomation_Events = ET.SubElement(x_ArrangerAutomation, 'Events')
        x_ArrangerAutomation_AutomationTransformViewState = ET.SubElement(x_ArrangerAutomation, 'AutomationTransformViewState')
        addvalue(x_ArrangerAutomation_AutomationTransformViewState, 'IsTransformPending', 'false')
        ET.SubElement(x_ArrangerAutomation_AutomationTransformViewState, 'TimeAndValueTransforms')

        set_add_sequencer_end(x_AudioSequencer)

    do_device_data_instrument(cvpj_track_data, x_DeviceChain_i_Devices)
    do_device_data(cvpj_track_data, x_DeviceChain_i_Devices)

    x_DeviceChain_i_SignalModulations = ET.SubElement(x_DeviceChain_i, 'SignalModulations')

    if tracktype == 'returntrack':
        x_FreezeSequencer = ET.SubElement(xmltag, 'FreezeSequencer')
        set_add_sequencer_base(x_FreezeSequencer)
        ET.SubElement(x_FreezeSequencer, 'ClipSlotList')
        addvalue(x_FreezeSequencer, 'MonitoringEnum', '1')

        x_Sample = ET.SubElement(x_FreezeSequencer, 'Sample')
        x_ArrangerAutomation = ET.SubElement(x_Sample, 'ArrangerAutomation')
        x_ArrangerAutomation_Events = ET.SubElement(x_ArrangerAutomation, 'Events')
        x_ArrangerAutomation_AutomationTransformViewState = ET.SubElement(x_ArrangerAutomation, 'AutomationTransformViewState')
        addvalue(x_ArrangerAutomation_AutomationTransformViewState, 'IsTransformPending', 'false')
        ET.SubElement(x_ArrangerAutomation_AutomationTransformViewState, 'TimeAndValueTransforms')

        set_add_sequencer_end(x_FreezeSequencer)


# ---------------- Track Base ----------------

def set_add_trackbase(xmltag, cvpj_track_data, tracktype, TrackUnfolded, track_placements):
    global t_mrkr_timesig

    trackname = cvpj_track_data['name'] if 'name' in cvpj_track_data else 'noname'
    colorval = colors.closest_color_index(colorlist_one, cvpj_track_data['color']) if 'color' in cvpj_track_data else 27

    addvalue(xmltag, 'LomId', '0')
    addvalue(xmltag, 'LomIdView', '0')
    addvalue(xmltag, 'IsContentSelectedInDocument', 'false')
    addvalue(xmltag, 'PreferredContentViewMode', '0')
    x_TrackDelay = ET.SubElement(xmltag, 'TrackDelay')
    addvalue(x_TrackDelay, 'Value',  '0')
    addvalue(x_TrackDelay, 'IsValueSampleBased', 'false')
    x_name = ET.SubElement(xmltag, 'Name')
    if tracktype == 'master': addvalue(x_name, 'EffectiveName', "Master")
    else: addvalue(x_name, 'EffectiveName', trackname)
    addvalue(x_name, 'UserName', trackname)
    addvalue(x_name, 'Annotation', '')
    addvalue(x_name, 'MemorizedFirstClipName', '')
    addvalue(xmltag, 'Color', str(colorval))
    x_AutomationEnvelopes = ET.SubElement(xmltag, 'AutomationEnvelopes')

    x_Envelopes = ET.SubElement(x_AutomationEnvelopes, 'Envelopes')
    addvalue(xmltag, 'TrackGroupId', '-1')
    addvalue(xmltag, 'TrackUnfolded', TrackUnfolded)
    addLomId(xmltag, 'DevicesListWrapper', '0')
    addLomId(xmltag, 'ClipSlotsListWrapper', '0')
    addvalue(xmltag, 'ViewData', '{}')
    x_TakeLanes = ET.SubElement(xmltag, 'TakeLanes')
    x_TakeLanes_i = ET.SubElement(x_TakeLanes, 'TakeLanes')
    addvalue(x_TakeLanes, 'AreTakeLanesFolded', 'true')
    addvalue(xmltag, 'LinkedTrackGroupId', '-1')
    if tracktype in ['miditrack', 'audiotrack']: 
        addvalue(xmltag, 'SavedPlayingSlot', '-1')
        addvalue(xmltag, 'SavedPlayingOffset', '0')
        addvalue(xmltag, 'Freeze', 'false')
        addvalue(xmltag, 'VelocityDetail', '0')
        addvalue(xmltag, 'NeedArrangerRefreeze', 'true')
        addvalue(xmltag, 'PostProcessFreezeClips', '0')

    x_DeviceChain = ET.SubElement(xmltag, 'DeviceChain')
    create_devicechain(x_DeviceChain, cvpj_track_data, tracktype, track_placements, colorval)

    if tracktype  == 'miditrack': 
        addvalue(xmltag, 'ReWireSlaveMidiTargetId', '0')
        addvalue(xmltag, 'PitchbendRange', '96')

# ---------------------------------------------------------------- DawVert Plugin Func -------------------------------------------------------------

tracknum = 1

def ableton_make_midi_track(cvpj_trackid, track_placements):
    global tracknum

    cvpj_track_data = {}
    if cvpj_trackid in cvpj_l['track_data']: cvpj_track_data = cvpj_l['track_data'][cvpj_trackid]

    cvpj_trackplacements = notelist_data.sort(track_placements['notes']) if 'notes' in track_placements else []

    x_MidiTrack = addId(x_Tracks, 'MidiTrack', str(tracknum))
    set_add_trackbase(x_MidiTrack, cvpj_track_data, 'miditrack', 'true', cvpj_trackplacements)
    tracknum += 1

def ableton_make_audio_track(cvpj_trackid, track_placements):
    global tracknum

    cvpj_track_data = {}
    if cvpj_trackid in cvpj_l['track_data']: cvpj_track_data = cvpj_l['track_data'][cvpj_trackid]

    cvpj_trackplacements = notelist_data.sort(track_placements['audio']) if 'audio' in track_placements else []

    x_AudioTrack = addId(x_Tracks, 'AudioTrack', str(tracknum))
    set_add_trackbase(x_AudioTrack, cvpj_track_data, 'audiotrack', 'true', cvpj_trackplacements)
    tracknum += 1

def ableton_make_return_track(cvpj_returndata):
    global tracknum
    cvpj_trackplacements = []

    x_AudioTrack = addId(x_Tracks, 'ReturnTrack', str(tracknum))
    set_add_trackbase(x_AudioTrack, cvpj_returndata, 'returntrack', 'false', cvpj_trackplacements)
    tracknum += 1


# ---------------------------------------------------------------- DawVert Plugin -------------------------------------------------------------

class output_cvpj(base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'Ableton Live 11'
    def getshortname(self): return 'ableton'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': ['loop', 'loop_off', 'loop_adv'],
        'auto_nopl': True,
        'placement_audio_stretch': ['warp']
        }
    def getsupportedplugformats(self): return ['vst2', 'vst3']
    def getsupportedplugins(self): return ['sampler:single', 'sampler:multi', 'sampler:slicer', 'universal:compressor', 'universal:expander']
    def getfileextension(self): return 'als'
    def parse(self, convproj_json, output_file):
        global cvpj_l
        global x_Tracks
        global LaneHeight
        global t_mrkr_timesig
        global output_file_global
        global cvpj_bpm
        global master_returnid
        global unusednum
        global dataset

        output_file_global = output_file

        cvpj_l = json.loads(convproj_json)
        LaneHeight = 68

        dataset = data_dataset.dataset('./data_dset/ableton.dset')

        if 'bpm' in cvpj_l: cvpj_bpm = cvpj_l['bpm']
        else: cvpj_bpm = 120

        t_mrkr_timesig = {}
        t_mrkr_locater = {}

        track_master_data = {}
        master_returns = {}
        master_returnid = {}

        if 'track_master' in cvpj_l: 
            track_master_data = cvpj_l['track_master']
            if 'returns' in track_master_data: 
                master_returns = track_master_data['returns']

        sendnum = 1
        for master_return in master_returns:
            master_returnid[master_return] = sendnum
            sendnum += 1

        if 'timemarkers' in cvpj_l: 
            cvpj_timemarkers = cvpj_l['timemarkers']
            for cvpj_timemarker in cvpj_timemarkers:
                istimemarker = False
                if 'type' in cvpj_timemarker:
                    if cvpj_timemarker['type'] == 'timesig':
                        istimemarker = True
                if istimemarker == True:
                    if cvpj_timemarker['denominator'] in [1,2,4,8,16]:
                        cvpj_denominator = cvpj_timemarker['denominator']
                        if cvpj_denominator == 1: out_denominator = 0
                        if cvpj_denominator == 2: out_denominator = 1
                        if cvpj_denominator == 4: out_denominator = 2
                        if cvpj_denominator == 8: out_denominator = 3
                        if cvpj_denominator == 16: out_denominator = 4
                        t_mrkr_timesig[cvpj_timemarker['position']/4] = (out_denominator*99)+(cvpj_timemarker['numerator']-1)
                    else:
                        t_mrkr_timesig[cvpj_timemarker['position']/4] = 201
                    if 'name' in cvpj_timemarker: t_mrkr_locater[cvpj_timemarker['position']/4] = cvpj_timemarker['name']
                else:
                    t_mrkr_locater[cvpj_timemarker['position']/4] = cvpj_timemarker['name']

        # XML Ableton
        x_root = ET.Element("Ableton")
        x_root.set('MajorVersion', "5")
        x_root.set('MinorVersion', "11.0_433")
        x_root.set('Creator', "Ableton Live 11.0")
        x_root.set('Revision', "9dc150af94686f816d2cf27815fcf2907d4b86f8")
        
        # XML LiveSet
        x_LiveSet = ET.SubElement(x_root, "LiveSet")
        addvalue(x_LiveSet, 'NextPointeeId', str(counter_pointee.next()))
        addvalue(x_LiveSet, 'OverwriteProtectionNumber', '2816')
        addvalue(x_LiveSet, 'LomId', '0')
        addvalue(x_LiveSet, 'LomIdView', '0')

        x_Tracks = ET.SubElement(x_LiveSet, "Tracks")

        LaneHeight = 35
        for cvpj_trackid, cvpj_trackdata, track_placements in tracks_r.iter(cvpj_l):
            tracktype = cvpj_trackdata['type']
            if tracktype == 'instrument': ableton_make_midi_track(cvpj_trackid, track_placements)
            if tracktype == 'audio': ableton_make_audio_track(cvpj_trackid, track_placements)
            #print(cvpj_trackid)

        for master_return in master_returns:
            ableton_make_return_track(master_returns[master_return])


        x_MasterTrack = ET.SubElement(x_LiveSet, "MasterTrack")
        set_add_trackbase(x_MasterTrack, track_master_data, 'master', 'false', None)

        x_PreHearTrack = ET.SubElement(x_LiveSet, "PreHearTrack")
        set_add_trackbase(x_PreHearTrack, track_master_data, 'prehear', 'false', None)

        x_SendsPre = ET.SubElement(x_LiveSet, "SendsPre")
        for master_return in master_returnid:
            x_SendPreBool = ET.SubElement(x_SendsPre, "SendPreBool")
            x_SendPreBool.set('Id', str(master_returnid[master_return]))
            x_SendPreBool.set('Value', 'false')

        create_Scenes(x_LiveSet)

        loop_on, loop_start, loop_end = song.get_loopdata(cvpj_l, 'r')

        create_transport(x_LiveSet, str(loop_start/4), str(loop_end-loop_start/4), abl_bool_val[int(loop_on)])
        create_songmastervalues(x_LiveSet)
        ET.SubElement(x_LiveSet, "SignalModulations")
        addvalue(x_LiveSet, 'GlobalQuantisation', '4')
        addvalue(x_LiveSet, 'AutoQuantisation', '0')
        create_grid(x_LiveSet, 'Grid', 1, 16, 20, 2, 'true', 'false')
        create_scaleinformation(x_LiveSet)
        addvalue(x_LiveSet, 'InKey', 'false')
        addvalue(x_LiveSet, 'SmpteFormat', '0')
        create_timeselection(x_LiveSet, 0, 0)
        create_sequencernavigator(x_LiveSet)
        addvalue(x_LiveSet, 'ViewStateExtendedClipProperties', 'false')
        addvalue(x_LiveSet, 'IsContentSplitterOpen', 'true')
        addvalue(x_LiveSet, 'IsExpressionSplitterOpen', 'true')
        create_ExpressionLanes(x_LiveSet)
        create_ContentLanes(x_LiveSet)
        addvalue(x_LiveSet, 'ViewStateFxSlotCount', '4')
        addvalue(x_LiveSet, 'ViewStateSessionMixerHeight', '120')

        LocaterID = 0
        x_Locaters = create_Locators(x_LiveSet)
        for s_mrkr_locater in t_mrkr_locater:
            x_Locator = addId(x_Locaters, 'Locator', str(LocaterID))
            addvalue(x_Locator, 'LomId', 0)
            addvalue(x_Locator, 'Time', s_mrkr_locater)
            addvalue(x_Locator, 'Name', t_mrkr_locater[s_mrkr_locater])
            addvalue(x_Locator, 'Annotation', '')
            addvalue(x_Locator, 'IsSongStart', 'false')
            LocaterID += 1

        x_DetailClipKeyMidis = ET.SubElement(x_LiveSet, "DetailClipKeyMidis")
        addLomId(x_LiveSet, 'TracksListWrapper', '0')
        addLomId(x_LiveSet, 'VisibleTracksListWrapper', '0')
        addLomId(x_LiveSet, 'ReturnTracksListWrapper', '0')
        addLomId(x_LiveSet, 'ScenesListWrapper', '0')
        addLomId(x_LiveSet, 'CuePointsListWrapper', '0')
        addvalue(x_LiveSet, 'ChooserBar', '0')
        addvalue(x_LiveSet, 'Annotation', '')
        addvalue(x_LiveSet, 'SoloOrPflSavedValue', 'true')
        addvalue(x_LiveSet, 'SoloInPlace', 'true')
        addvalue(x_LiveSet, 'CrossfadeCurve', '2')
        addvalue(x_LiveSet, 'LatencyCompensation', '2')
        addvalue(x_LiveSet, 'HighlightedTrackIndex', '2')
        create_GroovePool(x_LiveSet)
        addvalue(x_LiveSet, 'AutomationMode', 'false')
        addvalue(x_LiveSet, 'SnapAutomationToGrid', 'true')
        addvalue(x_LiveSet, 'ArrangementOverdub', 'false')
        addvalue(x_LiveSet, 'ColorSequenceIndex', '1')
        create_AutoColorPickerForPlayerAndGroupTracks(x_LiveSet)
        create_AutoColorPickerForReturnAndMasterTracks(x_LiveSet)
        addvalue(x_LiveSet, 'ViewData', '{}')
        addvalue(x_LiveSet, 'MidiFoldIn', 'false')
        addvalue(x_LiveSet, 'MidiFoldMode', '0')
        addvalue(x_LiveSet, 'MultiClipFocusMode', 'false')
        addvalue(x_LiveSet, 'MultiClipLoopBarHeight', '0')
        addvalue(x_LiveSet, 'MidiPrelisten', 'false')
        x_LinkedTrackGroups = ET.SubElement(x_LiveSet, "LinkedTrackGroups")
        addvalue(x_LiveSet, 'AccidentalSpellingPreference', '3')
        addvalue(x_LiveSet, 'PreferFlatRootNote', 'false')
        addvalue(x_LiveSet, 'UseWarperLegacyHiQMode', 'false')
        set_add_VideoWindowRect(x_LiveSet)
        addvalue(x_LiveSet, 'ShowVideoWindow', 'true')
        addvalue(x_LiveSet, 'TrackHeaderWidth', '93')
        addvalue(x_LiveSet, 'ViewStateArrangerHasDetail', 'false')
        addvalue(x_LiveSet, 'ViewStateSessionHasDetail', 'true')
        addvalue(x_LiveSet, 'ViewStateDetailIsSample', 'false')
        create_viewstates(x_LiveSet)

        # Main

        xmlstr = minidom.parseString(ET.tostring(x_root)).toprettyxml(indent="\t")
        with open(output_file, "w") as f:
            f.write(xmlstr)