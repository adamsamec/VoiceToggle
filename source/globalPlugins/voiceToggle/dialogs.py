# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/>.

import addonHandler
from synthDrivers.silence import SynthDriver as SilenceSynthDriver
import ui
import gui

import wx
from .voiceToggle import voiceToggle, APP_VERSION, SILENCE_VOICE_NAME

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
