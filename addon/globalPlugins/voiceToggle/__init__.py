# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/gpl-2.0.html>.

import addonHandler
import globalPluginHandler
import scriptHandler
from synthDriverHandler import synthDoneSpeaking
import config
import gui

from .settingsDialogs import OptionsPanel
from .voiceToggle import VoiceToggle

addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self):
		super(GlobalPlugin, self).__init__()

		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(OptionsPanel)
		self.app = VoiceToggle()
		self.isSynthDoneSpeakingRegistered = False
		config.post_configProfileSwitch.register(self.app.handleProfileSwitch)

	def terminate(self):
		self.app.terminate()

	def __terminate__(self):
		super(GlobalPlugin, self).__terminate__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(OptionsPanel)

	@scriptHandler.script(
		# Translators: Gesture description for the Input gestures settings dialog
		description=_("Switches to the next voice."),
		category = _("Voice Toggle"),
	)
	def script_toggleVoice(self, gesture):
		if not self.isSynthDoneSpeakingRegistered:
			synthDoneSpeaking.register(self.app.handleDoneSpeaking)
			self.isSynthDoneSpeakingRegistered = True
		if len(self.app.voiceSettings) == 0:
			return
		nextIndex = self.app.getNextVoiceSettingsIndex(self.app.currentVoiceSettingsIndex)
		newIndex = self.app.changeVoice(nextIndex)
		self.app.currentVoiceSettingsIndex = newIndex

	@scriptHandler.script(
		# Translators: Gesture description for the Input gestures settings dialog
		description=_("Switches to the previous voice."),
		category = _("Voice Toggle"),
	)
	def script_previousVoice(self, gesture):
		if not self.isSynthDoneSpeakingRegistered:
			synthDoneSpeaking.register(self.app.handleDoneSpeaking)
		self.isSynthDoneSpeakingRegistered = True
		if len(self.app.voiceSettings) == 0:
			return
		previousIndex = self.app.getPreviousVoiceSettingsIndex(self.app.currentVoiceSettingsIndex)
		newIndex = self.app.changeVoice(previousIndex)
		self.app.currentVoiceSettingsIndex = newIndex
