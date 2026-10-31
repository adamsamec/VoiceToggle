# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/gpl-2.0.html>.

import addonHandler
from synthDrivers.silence import SynthDriver as SilenceSynthDriver
import gui

import wx

addonHandler.initTranslation()

class SelectVoiceDialog(wx.Dialog):
	_instance = None

	def __new__(cls, *args, **kwargs):
		if SelectVoiceDialog._instance is None:
			return super(SelectVoiceDialog, cls).__new__(cls, *args, **kwargs)
		return SelectVoiceDialog._instance

	def __init__(self, parent, app):
		if SelectVoiceDialog._instance is not None:
			return
		SelectVoiceDialog._instance = self

		super(SelectVoiceDialog, self).__init__(parent, title=_("Select a voice"))
		self.app = app

		self.Bind(wx.EVT_CHAR_HOOK, self.charHook)
		self.addWidgets()

	def addWidgets(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, wx.VERTICAL)

		# Translators: Label for the voices listbox in the Select a voice dialog
		self.voicesListBox = sHelper.addLabeledControl(_("Voices"), wx.ListBox, choices=[])
		self.initVoicesListBox()

		# Buttons group
		buttons = gui.guiHelper.ButtonHelper(wx.VERTICAL)

		# Translators: Label for the OK button in the select a voice dialog
		self.okButton = buttons.addButton(self, label=_("OK"))
		self.okButton.Bind(wx.EVT_BUTTON, self.onOkButtonClick)
		self.okButton.SetDefault()

		# Translators: Label for the cancel button in the select voice dialog
		cancelButton = buttons.addButton(self, label=_("Cancel"))
		cancelButton.Bind(wx.EVT_BUTTON, self.onCancelButtonClick)
		
		sHelper.addItem(buttons)
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)

	def initVoicesListBox(self):
		listBoxItems = []
		voiceSettings = self.app.getVoiceSettings()
		for voiceSetting in voiceSettings:
			synthName = self.app.getSynthNameById(voiceSetting["synthId"])
			voiceName = self.app.getVoiceNameById(voiceSetting["synthId"], voiceSetting["voiceId"])
			choice = synthName if voiceSetting["synthId"] == SilenceSynthDriver.name else f"{voiceName} ({synthName})"
			listBoxItems.append(choice)
		self.voicesListBox.SetItems(listBoxItems)

	def charHook(self, event):
		key = event.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.close()
		else:
			event.Skip()

	def onOkButtonClick(self, event):
		self.app.changeVoice(self.voicesListBox.GetSelection())
		self.close()

	def onCancelButtonClick(self, event):
		self.close()

	def close(self):
		self.Destroy()
		SelectVoiceDialog._instance = None
