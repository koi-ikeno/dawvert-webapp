# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import lxml.etree as ET
from dawvertplus.functions import plugin_vst2
from dawvertplus.functions_plugdata import data_vc2xml

class juicysfplugin_data:
	def __init__(self, cvpj_plugindata):
		self.cvpj_plugindata = cvpj_plugindata
		self.jsfp_xml = ET.Element("MYPLUGINSETTINGS")
		self.jsfp_params = ET.SubElement(self.jsfp_xml, "params")
		self.jsfp_uiState = ET.SubElement(self.jsfp_xml, "uiState")
		self.jsfp_soundFont = ET.SubElement(self.jsfp_xml, "soundFont")
		self.jsfp_params.set('bank', "0")
		self.jsfp_params.set('preset', "0")
		self.jsfp_params.set('attack', "0.0")
		self.jsfp_params.set('decay', "0.0")
		self.jsfp_params.set('sustain', "0.0")
		self.jsfp_params.set('release', "0.0")
		self.jsfp_params.set('filterCutOff', "0.0")
		self.jsfp_params.set('filterResonance', "0.0")
		self.jsfp_uiState.set('width', "500.0")
		self.jsfp_uiState.set('height', "300.0")
		self.jsfp_soundFont.set('path', '')

	def set_bankpatch(self, bank, patch, filename):
		self.jsfp_params.set('bank', str(bank/128))
		self.jsfp_params.set('preset', str(patch/128))
		self.jsfp_soundFont.set('path', filename)

	def set_param(self, name, value):
		self.jsfp_params.set(name, str(value))

	def set_sffile(self, value):
		self.jsfp_soundFont.set('path', value)

	def to_cvpj_vst2(self, cvpj_plugindata):
		plugin_vst2.replace_data(self.cvpj_plugindata, 'name','any', 'juicysfplugin', 'chunk', data_vc2xml.make(self.jsfp_xml), None)