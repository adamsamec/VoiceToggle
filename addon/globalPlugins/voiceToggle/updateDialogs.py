# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/>.

import addonHandler
import gui

import wx

addonHandler.initTranslation()

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
		currentVersion = addonHandler.getCodeAddon().version
		updateAvailableLabel = _("VoiceToggle add-on for NVDA version {latestVersion} is available, you have {currentVersion}. Do you want to download and install the update now?").format(latestVersion=self.update["version"], currentVersion=currentVersion)
		updateAvailableText = sHelper.addItem(wx.StaticText(self, label=updateAvailableLabel))

		# Check for update on NVDA start checkbox
		if self.displayCheckOnStartCheckbox:
			self.checkUpdateOnStartCheckbox = sHelper.addItem(wx.CheckBox(self, label=_("Automatically check for update on NVDA start")))
			self.checkUpdateOnStartCheckbox.Bind(wx.EVT_CHECKBOX, self.onCheckUpdateOnStartCheckChange)
			self.checkUpdateOnStartCheckbox.SetValue(self.app.isCheckUpdateOnStart)

		# Buttons group
		buttons = gui.guiHelper.ButtonHelper(wx.VERTICAL)

		# Translators: Label for the update button in the update available dialog
		self.updateButton = buttons.addButton(self, label=_("Update"))
		self.updateButton.Bind(wx.EVT_BUTTON, self.onUpdateButtonClick)
		self.updateButton.SetDefault()
		self.updateButton.SetFocus()

		# Translators: Label for the close button in the update available dialog
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
		currentVersion = addonHandler.getCodeAddon().version
		upToDateLabel = _("VoiceToggle version {currentVersion} is up to date.").format(currentVersion=currentVersion)
		upToDateText = sHelper.addItem(wx.StaticText(self, label=upToDateLabel))

		# Translators: Label for the close button in the up to date dialog
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

		errorLabel = _("Check for update for the VoiceToggle add-on was not successful. Please verify that you are connected to the Internet.")
		errorText = sHelper.addItem(wx.StaticText(self, label=errorLabel))

		# Translators: Label for the close button in the update check error dialog
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
