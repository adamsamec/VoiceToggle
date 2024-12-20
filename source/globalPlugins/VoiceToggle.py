# Copyright 2024 Adam Samec <adam.samec@gmail.com>

import globalPluginHandler
import speech
try:
	from speech import getSynth, setSynth
except ImportError:
	from synthDriverHandler import getSynth, setSynth, getSynthList, getSynthInstance
	from synthDrivers.silence import SynthDriver as SilenceSynthDriver
import addonHandler
import config
import ui
import gui

import json
from threading import Thread
import wx

addonHandler.initTranslation()

# Constants
SILENCE_VOICE_NAME = _("Silence")
ONECORE_SYNTH_ID = "oneCore"
CONFIG_SPEC = {
	"voiceSettings": "string_list(default=list())",
	"currentVoiceSettingsIndex": "integer(default=0)",
}
SAVED_PARAMS = ["volume", "rate", "pitch"]

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
	title = _("VoiceToggle")

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
		voiceToggle.deleteInvalidVoiceSettings()
		voiceToggle.updateVoiceSetting()
		self.voiceSettings = voiceToggle.getVoiceSettings()

	def updateVoicesListBox(self, selectionIndex=0):
		self.voicesListBox.Clear()
		if len(self.voiceSettings) == 0:
			self.voicesListBox.Append(_("No voices added yet"))
			self.voicesListBox.SetSelection(0)
			return
		for index, voiceSetting in enumerate(self.voiceSettings):
			choice = voiceSetting["synthName"] if voiceSetting["synthId"] == SilenceSynthDriver.name else f"{voiceSetting['voiceName']} ({voiceSetting['synthName']})"

			# First voice is the default one
			if index == 0:
				choice = _("Default") + ": " + choice
			self.voicesListBox.Append(choice)
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
		selectionIndex = self.voicesListBox.GetSelection()
		if selectionIndex == 0:
			ui.message(_("Default voice cannot be removed"))
			return
		del self.voiceSettings[selectionIndex]
		newSelectionIndex = max(0, min(selectionIndex, len(self.voiceSettings) - 1))
		self.updateVoicesListBox(newSelectionIndex)
		self.updateRemoveButtonState()
		self.isVoiceSettingsModified = True

	def updateRemoveButtonState(self):
		if len(self.voiceSettings) > 0:
			self.removeVoiceButton.Enable()
		else:
			self.removeVoiceButton.Disable()

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

		# Synth ComboBox
		synthsNames = [instance["name"] for instance in voiceToggle.getSynthsInstances()]
		self.synthComboBox = sHelper.addLabeledControl(_("Synthesizer"), wx.Choice, choices=synthsNames)
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
		self.voiceComboBox.Clear()
		synthSelection = self.synthComboBox.GetSelection()
		self.voicesIds = []
		synthsInstances = voiceToggle.getSynthsInstances()
		self.synthsIds = [instance["id"] for instance in synthsInstances ]
		synthId = self.synthsIds[synthSelection]		

		# Special treatment for silence synth
		if synthId == SilenceSynthDriver.name:
			self.voicesIds.append(SilenceSynthDriver.name)
			self.voiceComboBox.Append(SILENCE_VOICE_NAME)
		else:
			voices = next(instance["instance"].availableVoices  for instance in synthsInstances if instance["id"] == synthId)
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
			"synthId": self.synthsIds[self.synthComboBox.GetSelection()],
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
		self.preloadSynthInstances()
		self.voiceSettings = []
		self.isVoiceSettingsModified = False
		self.loadVoiceSettingsFromConfig()

		# Create the default voice setting if does not exist, but only for other than OneCore synths
		if len(self.voiceSettings) == 0:
			self.currentVoiceSettingsIndex = 0
			voiceSetting = self.getFreshVoiceSetting()
			if voiceSetting != None:
				self.voiceSettings.append(voiceSetting)
		
	def preloadSynthInstances(self):
		origSynthId = getSynth().name
		self.synthsInstances = []
		synthsInfos = getSynthList()

		# setSynth("oneCore") throws strange error, so skip it
		"""
		# getSynthInstance("oneCore")throws strange error if retrieved after another getSynthinstance call, so call it first
		synthInstance = getSynthInstance(ONECORE_SYNTH_ID, asDefault=True)
		self.synthsInstances.append({
			"id": ONECORE_SYNTH_ID,
			"name": next(synthInfo[1] for synthInfo in synthsInfos if synthInfo[0] == ONECORE_SYNTH_ID),
			"instance": synthInstance
		})
"""

		# Save other synth instances
		for synthInfo in synthsInfos:
			synthId = synthInfo[0]
			isSilence = synthId == SilenceSynthDriver.name
			synthName = SILENCE_VOICE_NAME if isSilence else synthInfo[1]
			if synthId == ONECORE_SYNTH_ID:
				continue
			instance = None if isSilence else getSynthInstance(synthId)
			self.synthsInstances.append({
				"id": synthId,
				"name": synthName,
				"instance": instance
			})

		# Resetting synth fixes the bug of broken ring after calling getSynthInstance()
		setSynth(origSynthId)

	def getSynthsInstances(self):
		return self.synthsInstances

	def loadVoiceSettingsFromConfig(self):
		self.voiceSettings = [json.loads(voiceSetting) for voiceSetting in self.getConfig("voiceSettings")]
		self.currentVoiceSettingsIndex = self.getConfig("currentVoiceSettingsIndex")
		if len(self.voiceSettings) == 0:
			self.currentVoiceSettingsIndex = -1

	def saveVoiceSettingsTOConfig(self):
		voiceSettingsJson = [json.dumps(voiceSetting) for voiceSetting in self.voiceSettings] 
		self.setConfig("voiceSettings", voiceSettingsJson)
		self.setConfig("currentVoiceSettingsIndex", self.currentVoiceSettingsIndex)

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
		nextIndex = self.getNextVoiceSettingsIndex(self.currentVoiceSettingsIndex)
		newIndex = self.changeVoice(nextIndex)
		self.currentVoiceSettingsIndex = newIndex

	def getNextVoiceSettingsIndex(self, index):
		voiceSettingsLength = len(self.voiceSettings)
		if voiceSettingsLength == 0:
			return -1
		
		# If index out of list bounds and not empty, return zero
		if index < 0 or index >= voiceSettingsLength:
			return 0
		newIndex = (index + 1) % voiceSettingsLength
		return newIndex

	def changeVoice(self, newIndex, announceChange=True):
		voiceSettingsLength = len(self.voiceSettings)
		if (newIndex >= voiceSettingsLength) or (newIndex < 0):
			if voiceSettingsLength > 0:
				return 0
			else:
				return -1
		newVoiceSetting = self.voiceSettings[newIndex]

		# Delete all invalid voice settings starting from the new index, and update the new index if necessary
		newIndex = self.deleteInvalidVoiceSettings(startIndex=newIndex, dontChangeVoice=True)
		newVoiceSetting = self.voiceSettings[newIndex]

		synth = getSynth()

		# To prevent mismatch, don't update current synth, voice and speech params if voice settings have been modified in NVDA settings, or if changed voice settings due to invalidation
		currentVoiceSetting = None if self.isVoiceSettingsModified else self.updateVoiceSetting()
		
		# Only apply new synth if voice settings have been modified in add-on settings, if changed from previous one, or if is OneCore voice and new is not
		if (currentVoiceSetting == None) or (newVoiceSetting["synthId"] != currentVoiceSetting["synthId"]) or (newVoiceSetting["synthId"] != ONECORE_SYNTH_ID and synth.name == ONECORE_SYNTH_ID):
			if newVoiceSetting["synthId"] == SilenceSynthDriver.name:
				setSynth(None)
			else:
				setSynth(newVoiceSetting["synthId"])
				synth = getSynth()
		
		# Apply new voice setting
		if newVoiceSetting["synthId"] != SilenceSynthDriver.name:
			synth.voice = newVoiceSetting["voiceId"]
			for param in SAVED_PARAMS:
				if param in newVoiceSetting:
					setattr(synth, param, newVoiceSetting[param])
			if synth != None:
				synth.saveSettings()
		if announceChange:
			ui.message(newVoiceSetting["voiceName"])
		self.isVoiceSettingsModified = False
		return newIndex

	def deleteInvalidVoiceSettings(self, startIndex=0, dontChangeVoice=False):
		newValidIndex = startIndex
		doChangeVoice = False

		# Start deleting from start index
		index = self.findNextInvalid(startIndex)

		voiceSettingsLength = len(self.voiceSettings)
		while voiceSettingsLength > 0 and index >= 0:
			del self.voiceSettings[index]
			voiceSettingsLength = len(self.voiceSettings)

			# If some setting before the current one has been deleted, shift the current index to the previous index and change the voice
			if index < self.currentVoiceSettingsIndex:
				self.currentVoiceSettingsIndex -= 1
				doChangeVoice = True

			# If setting at the same index as the current setting has been deleted, change the voice
			elif index == self.currentVoiceSettingsIndex:
				doChangeVoice = True
				
			# If some setting before the start index has been deleted, shift the new valid index to the previous index
			if index < startIndex:
				newValidIndex -= 1

			index = self.findNextInvalid(index)

		# Check if list has been deleted entirely or was originally empty
		if voiceSettingsLength == 0:
			self.currentVoiceSettingsIndex = -1
			return -1
		
		if doChangeVoice and not dontChangeVoice:
			self.isVoiceSettingsModified = True
			self.changeVoice(self.currentVoiceSettingsIndex, announceChange=False)

		return newValidIndex

	def findNextInvalid(self, startIndex):
		# If start index is out of list bounds, start at zero
		if startIndex < 0 or startIndex >= len(self.voiceSettings):
			startIndex = 0

		index = startIndex
		while index >= 0 and self.synthAndVoiceExist(self.voiceSettings[index]):
			# If list is empty, return not found
			if len(self.voiceSettings) == 0:
				return -1
			index = self.getNextVoiceSettingsIndex(index)

			# If we are back on start, we have traversed entire list, so return not found
			if index == startIndex:
				return -1
		return index


	def synthAndVoiceExist(self, voiceSetting):
		synthExists = False
		voiceExists = False
		synthInstances = self.getSynthsInstances()
		for instance in synthInstances:
			if instance["id"] == voiceSetting["synthId"]:
				synthExists = True
				for voiceId in instance["instance"].availableVoices:
					if voiceId == voiceSetting["voiceId"]:
						voiceExists = True
						break
				else:
					continue
				break # Executed only if inner loop broke
		return synthExists and voiceExists

	def updateVoiceSetting(self):
		if self.currentVoiceSettingsIndex < 0 or len(self.voiceSettings) <= self.currentVoiceSettingsIndex:
			return None
		currentVoiceSetting = self.voiceSettings[self.currentVoiceSettingsIndex]
		synth = getSynth()
		isSilenceFresh = synth == None
		if not isSilenceFresh:
			for param in SAVED_PARAMS:
				currentVoiceSetting[param] = getattr(synth, param)

		# Determine and update fresh synth and voice names only when synth or voice ID changed
		isChangeToSilence = isSilenceFresh and currentVoiceSetting["synthId"] != SilenceSynthDriver.name
		isSynthOrVoiceChange = not isSilenceFresh and (synth.name != currentVoiceSetting["synthId"] or synth.voice != currentVoiceSetting["voiceId"])
		if isChangeToSilence or isSynthOrVoiceChange:
			freshVoiceSetting = self.getFreshVoiceSetting()
			self.voiceSettings[self.currentVoiceSettingsIndex] = {**currentVoiceSetting, **freshVoiceSetting}

		return currentVoiceSetting

	def getFreshVoiceSetting(self):
		synth = getSynth()
		if synth.name == ONECORE_SYNTH_ID:
			if len(self.voiceSettings) == 0:
				return None
			currentVoiceSetting = self.voiceSettings[self.currentVoiceSettingsIndex]
			synthId = currentVoiceSetting["synthId"]
		else:
			currentVoiceSetting = None
			synthId = SilenceSynthDriver.name if synth == None else synth.name
		synthInstance = next(instance for instance in self.getSynthsInstances() if instance["id"] == synthId)
		if synthId == SilenceSynthDriver.name:
			voiceId = SilenceSynthDriver.name
			voiceName = SILENCE_VOICE_NAME
		else:
			if synth.name == ONECORE_SYNTH_ID:
				voiceId = currentVoiceSetting["voiceId"]
			else:
				voiceId = synth.voice
			voices = synthInstance["instance"].availableVoices
			voiceName = next(voices[id].displayName for id in voices if id == voiceId)
		voiceSetting = {
			"synthId": synthId,
			"synthName": synthInstance["name"],
			"voiceId": voiceId,
			"voiceName": voiceName
		}
		return voiceSetting

	def terminate(self):
		# Save current synth, voice and speech params before terminating
		if len(self.voiceSettings) > 0 and not self.isVoiceSettingsModified:
			self.updateVoiceSetting()
			
		self.saveVoiceSettingsTOConfig()

	def getConfig(self, key):
		return config.conf["VoiceToggle"][key]

	def setConfig(self, key, value):
		config.conf["VoiceToggle"][key] = value

voiceToggle = VoiceToggle()
