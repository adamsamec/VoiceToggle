# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/>.

import addonHandler
from synthDrivers.silence import SynthDriver as SilenceSynthDriver
import ui
import gui

import wx

import globalPlugins.voiceToggle.consts as consts
from .voiceToggle import voiceToggle
from .updateDialogs import UpdateAvailableDialog, UpToDateDialog, UpdateCheckErrorDialog

addonHandler.initTranslation()

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
		voiceToggle.cleanUpVoiceSettings()
		# voiceToggle.updateVoiceSetting()
		self.voiceSettings = voiceToggle.getVoiceSettings()

	def updateVoicesListBox(self, selectionIndex=0):
		self.voicesListBox.Clear()
		if len(self.voiceSettings) == 0:
			self.voicesListBox.Append(_("No voices added yet"))
			self.voicesListBox.SetSelection(0)
			return
		for index, voiceSetting in enumerate(self.voiceSettings):
			synthName = voiceToggle.getSynthNameById(voiceSetting["synthId"])
			voiceName = voiceToggle.getVoiceNameById(voiceSetting["synthId"], voiceSetting["voiceId"])
			choice = synthName if voiceSetting["synthId"] == SilenceSynthDriver.name else f"{voiceName} ({synthName})"

			# First voice is the default one
			if index == 0:
				# Translators: Default text prepended to the voice and synth name in listbox
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
		voiceToggle.updateSynthsWithVoices()
		synthsWithVoices = voiceToggle.getSynthsWithVoices()
		self.synthsIds = [synthWithVoices["id"] for synthWithVoices in synthsWithVoices]
		synthsNames = [synthWithVoices["name"] for synthWithVoices in synthsWithVoices]
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
		synthId = self.synthsIds[synthSelection]		
		self.voicesIds = []
		if synthId == SilenceSynthDriver.name:
		# Special treatment for silence synth
			self.voicesIds.append(SilenceSynthDriver.name)
			self.voiceComboBox.Append(consts.SILENCE_VOICE_NAME)
		else:
			voices = voiceToggle.getVoicesForSynth(synthId)
			for voice in voices:
				self.voicesIds.append(voice["id"])
				self.voiceComboBox.Append(voice["name"])
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
			"voiceId": self.voicesIds[self.voiceComboBox.GetSelection()],
		}
		self.plugin.addVoiceSetting(voiceSetting)
		self.close()

	def onCancelButtonClick(self, event):
		self.close()

	def close(self):
		self.Destroy()
