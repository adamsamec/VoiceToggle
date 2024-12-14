# Copyright 2024 Adam Samec <adam.samec@gmail.com>

import globalPluginHandler
import speech
try:
	from speech import getSynth, setSynth
except ImportError:
	from synthDriverHandler import getSynth, setSynth, getSynthList, getSynthInstance
import config
import ui
import gui

import json
from threading import Thread
import wx

CONFIG_SPEC = {
	"voiceSettings": "string_list(default=list())"
}

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self):
		super(GlobalPlugin, self).__init__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(OptionsPanel)

	def terminate(self):
		voiceToggle.terminate()

	def __terminate__(self):
		super(GlobalPlugin, self).__terminate__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(OptionsPanel)

	def script_toggleVoice(self, gesture):
		voiceToggle.toggleVoice()
	script_toggleVoice.__doc__ = _("Toggles to the next voice.")


	__gestures={
		"kb:NVDA+Alt+V": "toggleVoice"
	}

class OptionsPanel(gui.SettingsPanel):
	title = _("Voice Toggle Settings")

	def makeSettings(self, settingsSizer):
		self.loadVoiceSettings()
		self.isVoiceSettingsModified = False

		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		# Voices ListBox
		self.voicesListBox = sHelper.addLabeledControl(_("Voices"), wx.ListBox, choices=[])
		self.updateVoicesListBox()
		
		# Buttons group
		buttons = gui.guiHelper.ButtonHelper(wx.VERTICAL)

		# Add voice button
		self.addVoiceButton = buttons.addButton(self, label=_("Add voice"))
		self.addVoiceButton.Bind(wx.EVT_BUTTON, self.onAddVoiceButtonClick)

		# Remove voice button
		self.removeVoiceButton = buttons.addButton(self, label=_("Remove voice"))
		self.removeVoiceButton.Bind(wx.EVT_BUTTON, self.onRemoveVoiceButtonClick)
		self.updateRemoveButtonState()
		
		sHelper.addItem(buttons)

	def loadVoiceSettings(self):
		self.voiceSettings = voiceToggle.getVoiceSettings()

	def updateVoicesListBox(self, selectionIndex=0):
		self.voicesListBox.Clear()
		if len(self.voiceSettings) == 0:
			self.voicesListBox.Append(_("No voices added yet"))
			self.voicesListBox.SetSelection(0)
			return
		voicesChoices = [f"{voiceSetting['voiceName']} ({voiceSetting['synthName']})" for voiceSetting in self.voiceSettings]
		for voiceChoice in voicesChoices:
			self.voicesListBox.Append(voiceChoice)
		self.voicesListBox.SetSelection(selectionIndex)

	def addVoiceSetting(self, setting):
		insertIndex = 0 if len(self.voiceSettings) == 0 else self.voicesListBox.GetSelection() + 1
		self.voiceSettings.insert(insertIndex, setting)
		self.updateVoicesListBox(insertIndex)
		self.updateRemoveButtonState()
		self.isVoiceSettingsModified = True

	def onAddVoiceButtonClick(self, event):
		parent = event.GetEventObject().GetParent()
		addVoiceDialog = AddVoiceDialog(parent, self)
		addVoiceDialog.ShowModal()

	def onRemoveVoiceButtonClick(self, event):
		if len(self.voiceSettings) == 0:
			return
		selectionIndex = self.voicesListBox.GetSelection()
		del self.voiceSettings[selectionIndex]
		newSelectionIndex = max(0, min(selectionIndex, len(self.voiceSettings) - 1))
		self.updateVoicesListBox(newSelectionIndex)
		if not self.updateRemoveButtonState():
			self.addVoiceButton.SetFocus()
		self.isVoiceSettingsModified = True

	def updateRemoveButtonState(self):
		doEnable = len(self.voiceSettings) > 0
		if doEnable:
			self.removeVoiceButton.Enable()
		else:
			self.removeVoiceButton.Disable()
		return doEnable

	def onSave(self):
		if self.isVoiceSettingsModified:
			voiceToggle.markVoiceSettingsAsModified()
			self.isVoiceSettingsModified = False
		voiceToggle.setVoiceSettings(self.voiceSettings)

class AddVoiceDialog(wx.Dialog):

	def __init__(self, parent, plugin):
		super().__init__(parent, title=_("Add voice"))
		self.plugin = plugin

		self.Bind(wx.EVT_CHAR_HOOK, self.charHook)
		self.addWidgets()
		self.synthComboBox.SetFocus()

	def addWidgets(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, wx.VERTICAL)

		# Synthesiser ComboBox
		# Filter out the "oneCore" synth which sometimes throws exception for getSynthInstance("oneCore") call
		allSynthsInfos = getSynthList()
		self.synthsInfos = []
		for synthInfo in allSynthsInfos:
			if synthInfo[0] != "oneCore":
				self.synthsInfos.append(synthInfo)
		
		synthsNames = [synthInfo[1]for synthInfo in self.synthsInfos]
		self.synthComboBox = sHelper.addLabeledControl(_("Synthesiser"), wx.Choice, choices=synthsNames)
		self.synthComboBox.Select(0)
		self.synthComboBox.Bind(wx.EVT_CHOICE, self.onSynthChange)

		# Voice ComboBox
		self.voiceComboBox = sHelper.addLabeledControl(_("Voice"), wx.Choice, choices=[])
		self.updateVoiceComboBox()

		# Buttons group
		buttons = gui.guiHelper.ButtonHelper(wx.VERTICAL)

		# Add button
		addButton = buttons.addButton(self, label=_("Add"))
		addButton.Bind(wx.EVT_BUTTON, self.onAddButtonClick)
		addButton.SetDefault()

		# Cancel button
		cancelButton = buttons.addButton(self, label=_("Cancel"))
		cancelButton.Bind(wx.EVT_BUTTON, self.onCancelButtonClick)
		cancelButton.SetFocus()
		
		sHelper.addItem(buttons)
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)

	def onSynthChange(self, event):
		self.updateVoiceComboBox()

	def updateVoiceComboBox(self):
		synthSelection = self.synthComboBox.GetSelection()
		synthId = [synthInfo[0]for synthInfo in self.synthsInfos][synthSelection]
		synth = getSynthInstance(synthId)
		voices = synth.availableVoices
		self.voicesIds = []
		self.voiceComboBox.Clear()
		for voiceId in voices:
			self.voicesIds.append(voiceId)
			self.voiceComboBox.Append(voices[voiceId].displayName)
		self.voiceComboBox.Select(0)

	def charHook(self, event):
		key = event.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.close()
		else:
			event.Skip()

	def onAddButtonClick(self, event):
		voiceSetting = {
			"synthId": self.synthsInfos[self.synthComboBox.GetSelection()][0],
			"synthName": self.synthComboBox.GetStringSelection(),
			"voiceId": self.voicesIds[self.voiceComboBox.GetSelection()],
			"voiceName": self.voiceComboBox.GetStringSelection()
		}
		self.plugin.addVoiceSetting(voiceSetting)
		self.close()

	def onCancelButtonClick(self, event):
		self.close()

	def close(self):
		self.Destroy()

class VoiceToggle:

	def __init__(self):
		config.conf.spec["VoiceToggle"] = CONFIG_SPEC
		self.isVoiceSettingsModified = False
		self.loadVoiceSettingsFromConfig()

	def loadVoiceSettingsFromConfig(self):
		self.voiceSettings = [json.loads(voiceSetting) for voiceSetting in self.getConfig("voiceSettings")]
		self.currentIndex = 0

	def saveVoiceSettingsTOConfig(self):
		voiceSettingsJson = [json.dumps(voiceSetting) for voiceSetting in self.voiceSettings] 
		self.setConfig("voiceSettings", voiceSettingsJson)

	def getVoiceSettings(self):
		return self.voiceSettings.copy()

	def setVoiceSettings(self, settings):
		self.voiceSettings = settings.copy()
		self.saveVoiceSettingsTOConfig()

	def markVoiceSettingsAsModified(self):
		self.isVoiceSettingsModified = True

	def toggleVoice(self):
		if len(self.voiceSettings) == 0:
			return
		newIndex = (self.currentIndex +1) % len(self.voiceSettings)
		newVoiceSetting = self.voiceSettings[newIndex]

		# Don't update current voice setting rate if voice settings have been modified to prevent mismatch
		if self.isVoiceSettingsModified:
			currentVoiceSetting = None
		else:
			currentVoiceSetting = self.voiceSettings[self.currentIndex]
			currentVoiceSetting["rate"] = getSynth().rate
		
		# Only apply new synth if changed
		if (currentVoiceSetting == None) or (newVoiceSetting["synthId"] != currentVoiceSetting["synthId"]):
			setSynth(newVoiceSetting["synthId"])
		
		# Apply new voice setting
		synth = getSynth()
		synth.voice = newVoiceSetting["voiceId"]
		if "rate" in newVoiceSetting:
			synth.rate = newVoiceSetting["rate"]
		synth.saveSettings()

		ui.message(newVoiceSetting["voiceName"])
		self.currentIndex = newIndex
		self.isVoiceSettingsModified = False

	def terminate(self):
		# Save current speech rate before terminating
		if len(self.voiceSettings) > 0:
			self.voiceSettings[self.currentIndex]["rate"] = getSynth().rate
		self.saveVoiceSettingsTOConfig()

	def getConfig(self, key):
		return config.conf["VoiceToggle"][key]

	def setConfig(self, key, value):
		config.conf["VoiceToggle"][key] = value

voiceToggle = VoiceToggle()
