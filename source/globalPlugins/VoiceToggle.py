# Copyright 2025 Adam Samec <adam.samec@gmail.com>

import globalPluginHandler
from synthDriverHandler import getSynth, setSynth, getSynthList, getSynthInstance, synthDoneSpeaking
from synthDrivers.silence import SynthDriver as SilenceSynthDriver
import addonHandler
import api
import config
import ui
import gui

import json
import os
import shutil
from urllib.request import urlopen, urlretrieve, URLError
import wx

addonHandler.initTranslation()

# Constants
APP_VERSION = "1.2.1"
UPDATE_API_URL = "http://api.adamsamec.cz/nvda/VoiceToggle/Update.json"
TEMP_DIR = "..\\temp\\"

SILENCE_VOICE_NAME = _("Silence")
ONECORE_SYNTH_ID = "oneCore"

NORMAL_PROFILE_NAME = "[normal]"
CONFIG_SPEC = {
	"voiceSettings": "string_list(default=list())",
	"profilesVoiceSettingsIndeces": "string(default='{}')",
	"checkUpdateOnStart": "boolean(default=True)",
}
SAVED_PARAMS = ["volume", "rate", "pitch"]

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self):
		super(GlobalPlugin, self).__init__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(OptionsPanel)
		synthDoneSpeaking.register(voiceToggle.handleVoiceSettingChange)

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

		# Voices listbox
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

		# Check for update button
		checkForUpdateButton = sHelper.addItem(wx.Button(self, label=_("Check for update")))
		checkForUpdateButton.Bind(wx.EVT_BUTTON, self.onCheckForUpdateButtonClick)

		# Check for update on NVDA start checkbox
		self.checkUpdateOnStartCheckbox = sHelper.addItem(wx.CheckBox(self, label=_("Automatically check for update on NVDA start")))
		self.checkUpdateOnStartCheckbox.SetValue(voiceToggle.isCheckUpdateOnStart)

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

	def onCheckForUpdateButtonClick(self, event):
		parent = event.GetEventObject().GetParent()
		update = voiceToggle.checkForUpdate()
		if isinstance(update, dict):
			updateAvailableDialog = UpdateAvailableDialog(voiceToggle, update)
			updateAvailableDialog.Show()
		elif update == True:
			upToDateDialog = UpToDateDialog()
			upToDateDialog.Show()
		elif update == False:
			updateCheckErrorDialog = UpdateCheckErrorDialog()
			updateCheckErrorDialog.Show()

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
		voiceToggle.isCheckUpdateOnStart = self.checkUpdateOnStartCheckbox.GetValue()

class AddVoiceDialog(wx.Dialog):

	def __init__(self, parent, plugin):
		super().__init__(parent, title=_("Add voice"))
		self.plugin = plugin

		self.Bind(wx.EVT_CHAR_HOOK, self.charHook)
		self.addWidgets()

	def addWidgets(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, wx.VERTICAL)

		# Synth combobox
		synthsNames = [instance["name"] for instance in voiceToggle.getSynthsInstances()]
		self.synthComboBox = sHelper.addLabeledControl(_("Synthesizer"), wx.Choice, choices=synthsNames)
		self.synthComboBox.Select(0)
		self.synthComboBox.Bind(wx.EVT_CHOICE, self.onSynthChange)
		self.synthComboBox.SetFocus()

		# Voice combobox
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

class UpdateAvailableDialog(wx.Dialog):

	def __init__(self, app, update, displayCheckOnStartCheckbox=False):
		super().__init__(None, style=wx.DIALOG_NO_PARENT, title=_("VoiceToggle add-on update available"))
		self.app= app
		self.update = update
		self.displayCheckOnStartCheckbox = displayCheckOnStartCheckbox

		self.Bind(wx.EVT_CHAR_HOOK, self.charHook)
		self.addWidgets()

	def addWidgets(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, wx.VERTICAL)

		# Update available text
		updateAvailableLabel = _("VoiceToggle add-on for NVDA version {} is available, you have {}. Do you want to download and install the update now?").format(self.update["version"], APP_VERSION)
		updateAvailableText = sHelper.addItem(wx.StaticText(self, label=updateAvailableLabel))

		# Check for update on NVDA start checkbox
		if self.displayCheckOnStartCheckbox:
			self.checkUpdateOnStartCheckbox = sHelper.addItem(wx.CheckBox(self, label=_("Automatically check for update on NVDA start")))
			self.checkUpdateOnStartCheckbox.Bind(wx.EVT_CHECKBOX, self.onCheckUpdateOnStartCheckChange)
			self.checkUpdateOnStartCheckbox.SetValue(self.app.isCheckUpdateOnStart)

		# Buttons group
		buttons = gui.guiHelper.ButtonHelper(wx.VERTICAL)

		# Update button
		self.updateButton = buttons.addButton(self, label=_("Update"))
		self.updateButton.Bind(wx.EVT_BUTTON, self.onUpdateButtonClick)
		self.updateButton.SetDefault()
		self.updateButton.SetFocus()

		# Close button
		closeButton = buttons.addButton(self, label=_("Close"))
		closeButton.Bind(wx.EVT_BUTTON, self.onCloseButtonClick)
		
		sHelper.addItem(buttons)
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)

	def charHook(self, event):
		key = event.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.close()
		else:
			event.Skip()

	def onCheckUpdateOnStartCheckChange(self, event):
		self.app.isCheckUpdateOnStart = self.checkUpdateOnStartCheckbox.GetValue()

	def onUpdateButtonClick(self, event):
		self.app.downloadAndRunUpdate(self.update["addonUrl"])
		self.close()

	def onCloseButtonClick(self, event):
		self.close()

	def close(self):
		self.Destroy()

class UpToDateDialog(wx.Dialog):

	def __init__(self):
		super().__init__(None, style=wx.DIALOG_NO_PARENT, title=_("VoiceToggle is up to date"))

		self.Bind(wx.EVT_CHAR_HOOK, self.charHook)
		self.addWidgets()

	def addWidgets(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, wx.VERTICAL)

		# Up to date text
		upToDateLabel = _("VoiceToggle version {} is up to date.").format(APP_VERSION)
		upToDateText = sHelper.addItem(wx.StaticText(self, label=upToDateLabel))

		closeButton = sHelper.addItem(wx.Button(self, label=_("Close")))
		closeButton.Bind(wx.EVT_BUTTON, self.onCloseButtonClick)
		closeButton.SetDefault()
		
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)

	def charHook(self, event):
		key = event.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.close()
		else:
			event.Skip()

	def onCloseButtonClick(self, event):
		self.close()

	def close(self):
		self.Destroy()

class UpdateCheckErrorDialog(wx.Dialog):

	def __init__(self):
		super().__init__(None, style=wx.DIALOG_NO_PARENT, title=_("Check for update failed for VoiceToggle"))

		self.Bind(wx.EVT_CHAR_HOOK, self.charHook)
		self.addWidgets()

	def addWidgets(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, wx.VERTICAL)

		# Update check error text
		errorLabel = _("Check for update for the VoiceToggle add-on was not successful. Please verify that you are connected to the Internet.")
		errorText = sHelper.addItem(wx.StaticText(self, label=errorLabel))

		closeButton = sHelper.addItem(wx.Button(self, label=_("Close")))
		closeButton.Bind(wx.EVT_BUTTON, self.onCloseButtonClick)
		closeButton.SetDefault()
		
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)

	def charHook(self, event):
		key = event.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.close()
		else:
			event.Skip()

	def onCloseButtonClick(self, event):
		self.close()

	def close(self):
		self.Destroy()

class VoiceToggle:

	def __init__(self):
		config.conf.spec["VoiceToggle"] = CONFIG_SPEC

		currentDir = os.path.dirname(os.path.realpath(__file__))
		self.tempDirPath = os.path.join(currentDir, TEMP_DIR)
		self.isVoiceSettingsModified = False
		self.currentProfileName = NORMAL_PROFILE_NAME

		self.preloadSynthInstances()
		self.loadSettingsFromConfig()
		self.checkForUpdateOnStart()
		self.addDefaultVoiceSetting()
		self.alignCurrentVoiceSettingsIndex()

	@property
	def currentVoiceSettingsIndex(self):
		return self.profilesVoiceSettingsIndeces[self.currentProfileName]

	@currentVoiceSettingsIndex.setter
	def currentVoiceSettingsIndex(self, value):
		self.profilesVoiceSettingsIndeces[self.currentProfileName] = value

	def handleVoiceSettingChange(self):
		newProfileName = config.conf.profiles[-1].name
		if not newProfileName:
			newProfileName = NORMAL_PROFILE_NAME
		if not (newProfileName in self.profilesVoiceSettingsIndeces):
			self.profilesVoiceSettingsIndeces[newProfileName] = self.currentVoiceSettingsIndex
		self.currentProfileName = newProfileName
		self.alignCurrentVoiceSettingsIndex()

	def alignCurrentVoiceSettingsIndex(self):
		# This is an imperfect fix for cases when after switching to another profile or starting NVDA, the current synth and voice does not match the current voice setting
		synth = getSynth()
		currentVoiceSetting = self.voiceSettings[self.currentVoiceSettingsIndex]
		if currentVoiceSetting["synthId"] != synth.name or currentVoiceSetting["voiceId"] != synth.voice:
			for index, voiceSetting in enumerate(self.voiceSettings):
				if voiceSetting["synthId"] == synth.name and voiceSetting["voiceId"] == synth.voice:
					self.currentVoiceSettingsIndex = index
					break

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

	def loadSettingsFromConfig(self):
		self.voiceSettings = [json.loads(voiceSetting) for voiceSetting in self.getConfig("voiceSettings")]
		self.profilesVoiceSettingsIndeces = json.loads(self.getConfig("profilesVoiceSettingsIndeces"))
		self.isCheckUpdateOnStart = self.getConfig("checkUpdateOnStart")
		voiceSettingsLength = len(self.voiceSettings)
		if not (NORMAL_PROFILE_NAME in self.profilesVoiceSettingsIndeces):
			if voiceSettingsLength > 0:
				self.profilesVoiceSettingsIndeces[NORMAL_PROFILE_NAME] = 0
			else:
				self.profilesVoiceSettingsIndeces[NORMAL_PROFILE_NAME] = -1
		if voiceSettingsLength == 0:
			for profileName in self.profilesVoiceSettingsIndeces:
				self.profilesVoiceSettingsIndeces[profileName] = -1

	def saveSettingsTOConfig(self):
		voiceSettingsJson = [json.dumps(voiceSetting) for voiceSetting in self.voiceSettings] 
		self.setConfig("voiceSettings", voiceSettingsJson)
		self.setConfig("profilesVoiceSettingsIndeces", json.dumps(self.profilesVoiceSettingsIndeces))
		self.setConfig("checkUpdateOnStart", self.isCheckUpdateOnStart)

	def checkForUpdateOnStart(self):
		if self.isCheckUpdateOnStart:
			update = self.checkForUpdate()
			if isinstance(update, dict):
				updateAvailableDialog = UpdateAvailableDialog(self, update, displayCheckOnStartCheckbox=True)
				updateAvailableDialog.Show()
				updateAvailableDialog.Raise()

	def checkForUpdate(self):
		try:
			response = urlopen(UPDATE_API_URL)
			update = json.loads(response.read())

			# Compare the latest version with the current version
			if self.isUpdateAvailable(update["version"]):
				return update

			# True means we are up to date
			return True
		except URLError:
			pass
			
		# False means a request error occurred, such as no Internet
		return False

	def addDefaultVoiceSetting(self):
		# Create and add the default voice setting if does not exist, but only for other than OneCore synths
		if len(self.voiceSettings) == 0:
			self.currentVoiceSettingsIndex = 0
			voiceSetting = self.getFreshVoiceSetting()
			if voiceSetting != None:
				self.voiceSettings.append(voiceSetting)

	def getVoiceSettings(self):
		return self.voiceSettings.copy()

	def setVoiceSettings(self, settings):
		self.voiceSettings = settings.copy()
		self.saveSettingsTOConfig()

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
		
		# If index is out of list bounds and list is not empty, return zero
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
		
		# Determine the next voice setting
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
		if len(self.voiceSettings) == 0:
			return -1

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

	def getConfig(self, key):
		return config.conf["VoiceToggle"][key]

	def setConfig(self, key, value):
		config.conf["VoiceToggle"][key] = value

	def isUpdateAvailable(self, latestVersion):
		current = [int(part) for part in APP_VERSION.split(".")]
		latest = [int(part) for part in latestVersion.split(".")]
		isAvailable = latest[0] > current[0] or latest[1] > current[1] or latest[2] > current[2]
		return isAvailable

	def downloadAndRunUpdate(self, url):
		try:
			response = urlopen(url)

			# Get the filename from URL after redirect
			newFilename = os.path.basename(response.geturl())

			response = urlretrieve(url)

			# Copy the downloaded file from download directory to plugin temp directory
			downloadPath = response[0]
			newPath = os.path.join(self.tempDirPath, newFilename)
			shutil.copy2(downloadPath, newPath)
			
			# Run the file
			os.startfile(newPath)
			return True
		except Exception:
			pass
		return False

	def deleteTempFiles(self):
		for filename in os.listdir(self.tempDirPath):
			path = os.path.join(self.tempDirPath, filename)
			try:
				if os.path.isfile(path) or os.path.islink(path):
					os.unlink(path)
				elif os.path.isdir(path):
					shutil.rmtree(path)
					return True
			except Exception:
				pass
		return False

	def terminate(self):
		# Save current synth, voice and speech params before terminating
		if len(self.voiceSettings) > 0 and not self.isVoiceSettingsModified:
			self.updateVoiceSetting()
			
		self.saveSettingsTOConfig()
		self.deleteTempFiles()

# Create the app
voiceToggle = VoiceToggle()
