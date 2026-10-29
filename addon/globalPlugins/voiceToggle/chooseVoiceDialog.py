# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/gpl-2.0.html>.

import addonHandler
from synthDrivers.silence import SynthDriver as SilenceSynthDriver
import ui
import gui

import weakref
import wx

import globalPlugins.voiceToggle.consts as consts

addonHandler.initTranslation()

class ChooseVoiceDialog(wx.Dialog):

	def __init__(self, app):
		super().__init__(None, title=_("Choose voice"))
		self.app = app

		self.Bind(wx.EVT_CHAR_HOOK, self.charHook)
		self.addWidgets()

	def addWidgets(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, wx.VERTICAL)

		# Buttons group
		buttons = gui.guiHelper.ButtonHelper(wx.VERTICAL)

		# Translators: Label for the choose button in the choose voice dialog
		self.chooseButton = buttons.addButton(self, label=_("Choose"))
		self.chooseButton.Bind(wx.EVT_BUTTON, self.onChooseButtonClick)
		self.chooseButton.SetDefault()

		# Translators: Label for the cancel button in the choose voice dialog
		cancelButton = buttons.addButton(self, label=_("Cancel"))
		cancelButton.Bind(wx.EVT_BUTTON, self.onCancelButtonClick)
		
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

	def onChooseButtonClick(self, event):
		self.close()

	def onCancelButtonClick(self, event):
		self.close()

	def close(self):
		self.Destroy()
