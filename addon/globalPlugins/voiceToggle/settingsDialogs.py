# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/gpl-2.0.html>.

import addonHandler
from synthDrivers.silence import SynthDriver as SilenceSynthDriver
import ui
import gui
from gui.settingsDialogs import SettingsPanel

import weakref
import wx

import globalPlugins.voiceToggle.consts as consts

addonHandler.initTranslation()

class OptionsPanel(SettingsPanel):
	_app = None

	# Translators: Add-on settings panel title
	title = _("VoiceToggle")

	def __init__ (self, *args, **kwargs):
		self.app = self._app()
		SettingsPanel.__init__(self, *args, **kwargs)

		self.Bind(wx.EVT_WINDOW_DESTROY, self.Cleanup)

	def Cleanup (self, event=None):
		if hasattr(self, "app"):
			del self.app
		if event != None:
			event.Skip()

	def __del__ (self):
		self.Cleanup()

	@classmethod
	def setAppInstance (cls, instance):
		cls._app = weakref.ref(instance)

	def makeSettings(self, settingsSizer):
		self.loadSettings()
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

		# Translators: Label for the update voice by synth settings ring and speech settings dialog checkbox in the add-on settings
		self.updateVoicesCheckbox = sHelper.addItem(wx.CheckBox(self, label=_("Update voice when changed using the synth settings ring or speech settings dialog")))
		self.updateVoicesCheckbox.SetValue(self.otherSettings["enableVoiceUpdateByRingAndSpeechSettings"])

	def loadSettings(self):
		self.app.cleanUpVoiceSettings()
		self.voiceSettings = self.app.getVoiceSettings()
		self.otherSettings = self.app.getOtherSettings()

	def updateVoicesListBox(self, selectionIndex=0):
		listBoxItems = []
		for voiceSetting in self.voiceSettings:
			synthName = self.app.getSynthNameById(voiceSetting["synthId"])
			voiceName = self.app.getVoiceNameById(voiceSetting["synthId"], voiceSetting["voiceId"])
			choice = synthName if voiceSetting["synthId"] == SilenceSynthDriver.name else f"{voiceName} ({synthName})"
			listBoxItems.append(choice)
		self.voicesListBox.SetItems(listBoxItems)
		if len(listBoxItems) > 0:
			self.voicesListBox.SetSelection(selectionIndex)

	def addVoiceSetting(self, setting):
		insertIndex = 0 if len(self.voiceSettings) == 0 else self.voicesListBox.GetSelection() + 1
		self.voiceSettings.insert(insertIndex, setting)
		self.updateVoicesListBox(insertIndex)
		self.updateRemoveButtonState()
		self.isVoiceSettingsModified = True

	def onAddVoiceButtonClick(self, event):
		addVoiceDialog = AddVoiceDialog(self, self.app)
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
			self.app.applySettings(self.voiceSettings)
			self.isVoiceSettingsModified = False

		self.otherSettings["enableVoiceUpdateByRingAndSpeechSettings"] = self.updateVoicesCheckbox.GetValue()
		self.app.applyOtherSettingsAndSave(self.otherSettings)

class AddVoiceDialog(wx.Dialog):

	def __init__(self, parent, app):
		super().__init__(parent, title=_("Add voice"))
		self.plugin = parent
		self.app = app

		self.Bind(wx.EVT_CHAR_HOOK, self.charHook)
		self.addWidgets()

	def addWidgets(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, wx.VERTICAL)

		# Synth combobox
		self.app.updateSynthsWithVoices()
		synthsWithVoices = self.app.getSynthsWithVoices()
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
		comboBoxItems = []
		synthSelection = self.synthsComboBox.GetSelection()
		synthId = self.synthsIds[synthSelection]		
		self.voicesIds = []
		if synthId == SilenceSynthDriver.name:
		# Special treatment for silence synth
			self.voicesIds = [SilenceSynthDriver.name]
			comboBoxItems = [consts.SILENCE_VOICE_NAME]
		else:
			voices = self.app.getVoicesForSynth(synthId)
			for voice in voices:
				self.voicesIds.append(voice["id"])
				comboBoxItems.append(voice["name"])
		self.voicesComboBox.SetItems(comboBoxItems)
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
