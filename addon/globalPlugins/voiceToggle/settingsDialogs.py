# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/gpl-2.0.html>.

import addonHandler
from synthDrivers.silence import SynthDriver as SilenceSynthDriver
import ui
import gui
from gui.settingsDialogs import SettingsPanel

import wx

import globalPlugins.voiceToggle.consts as consts
from .voiceToggle import voiceToggle

addonHandler.initTranslation()

class OptionsPanel(SettingsPanel):
	# Translators: Add-on settings panel title
	title = _("VoiceToggle")

	def makeSettings(self, settingsSizer):
		self.loadVoiceSettings()
		self.isVoiceSettingsModified = False

		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		# Translators: Label for the voices listbox in the add-on settings
		self.voicesListBox = sHelper.addLabeledControl(_("Voices"), wx.ListBox, choices=[])
		self.updateVoicesListBox()
		
		# Buttons group
		buttons = gui.guiHelper.ButtonHelper(wx.VERTICAL)

		# Translators: Label for the add voice button in the add-on settings
		self.addVoiceButton = buttons.addButton(self, label=_("Add voice"))
		self.addVoiceButton.Bind(wx.EVT_BUTTON, self.onAddVoiceButtonClick)

		# Translators: Label for the remove voice button in the add-on settings
		self.removeVoiceButton = buttons.addButton(self, label=_("Remove voice"))
		self.removeVoiceButton.Bind(wx.EVT_BUTTON, self.onRemoveVoiceButtonClick)
		self.updateRemoveButtonState()

		sHelper.addItem(buttons)

	def loadVoiceSettings(self):
		voiceToggle.cleanUpVoiceSettings()
		self.voiceSettings = voiceToggle.getVoiceSettings()

	def updateVoicesListBox(self, selectionIndex=0):
		self.voicesListBox.Clear()
		if len(self.voiceSettings) == 0:
			# Translators: Message when no voices have been added yet in the voices listbox
			self.voicesListBox.Append(_("No voices added yet"))
			self.voicesListBox.SetSelection(0)
			return
		for voiceSetting in self.voiceSettings:
			synthName = voiceToggle.getSynthNameById(voiceSetting["synthId"])
			voiceName = voiceToggle.getVoiceNameById(voiceSetting["synthId"], voiceSetting["voiceId"])
			choice = synthName if voiceSetting["synthId"] == SilenceSynthDriver.name else f"{voiceName} ({synthName})"
			self.voicesListBox.Append(choice)
		self.voicesListBox.SetSelection(selectionIndex)

	def addVoiceSetting(self, setting):
		insertIndex = 0 if len(self.voiceSettings) == 0 else self.voicesListBox.GetSelection() + 1
		self.voiceSettings.insert(insertIndex, setting)
		self.updateVoicesListBox(insertIndex)
		self.updateRemoveButtonState()
		self.isVoiceSettingsModified = True

	def onAddVoiceButtonClick(self, event):
		addVoiceDialog = AddVoiceDialog(self)
		addVoiceDialog.ShowModal()

	def onRemoveVoiceButtonClick(self, event):
		if len(self.voiceSettings) == 1:
			ui.message(_("The last remaining voice cannot be removed"))
			return
		selectionIndex = self.voicesListBox.GetSelection()
		del self.voiceSettings[selectionIndex]
		newSelectionIndex = max(0, min(selectionIndex, len(self.voiceSettings) - 1))
		self.updateVoicesListBox(newSelectionIndex)
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

	def __init__(self, parent):
		super().__init__(parent, title=_("Add voice"))
		self.plugin = parent

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
		# Translators: Label for the synthesizers combobox in the add voice dialog
		self.synthsComboBox = sHelper.addLabeledControl(_("Synthesizer"), wx.Choice, choices=synthsNames)
		self.synthsComboBox.Select(0)
		self.synthsComboBox.Bind(wx.EVT_CHOICE, self.onSynthChange)
		self.synthsComboBox.SetFocus()

		# Translators: Label for the voices combobox in the add voice dialog
		self.voicesComboBox = sHelper.addLabeledControl(_("Voice"), wx.Choice, choices=[])
		self.updateVoiceComboBox()

		# Buttons group
		buttons = gui.guiHelper.ButtonHelper(wx.VERTICAL)

		# Translators: Label for the add button in the add voice dialog
		addButton = buttons.addButton(self, label=_("Add"))
		addButton.Bind(wx.EVT_BUTTON, self.onAddButtonClick)
		addButton.SetDefault()

		# Translators: Label for the cancel button in the add voice dialog
		cancelButton = buttons.addButton(self, label=_("Cancel"))
		cancelButton.Bind(wx.EVT_BUTTON, self.onCancelButtonClick)
		
		sHelper.addItem(buttons)
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)

	def onSynthChange(self, event):
		self.updateVoiceComboBox()

	def updateVoiceComboBox(self):
		self.voicesComboBox.Clear()
		synthSelection = self.synthsComboBox.GetSelection()
		synthId = self.synthsIds[synthSelection]		
		self.voicesIds = []
		if synthId == SilenceSynthDriver.name:
		# Special treatment for silence synth
			self.voicesIds.append(SilenceSynthDriver.name)
			self.voicesComboBox.Append(consts.SILENCE_VOICE_NAME)
		else:
			voices = voiceToggle.getVoicesForSynth(synthId)
			for voice in voices:
				self.voicesIds.append(voice["id"])
				self.voicesComboBox.Append(voice["name"])
		self.voicesComboBox.Select(0)

	def charHook(self, event):
		key = event.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.close()
		else:
			event.Skip()

	def onAddButtonClick(self, event):
		voiceSetting = {
			"synthId": self.synthsIds[self.synthsComboBox.GetSelection()],
			"voiceId": self.voicesIds[self.voicesComboBox.GetSelection()],
		}
		self.plugin.addVoiceSetting(voiceSetting)
		self.close()

	def onCancelButtonClick(self, event):
		self.close()

	def close(self):
		self.Destroy()
