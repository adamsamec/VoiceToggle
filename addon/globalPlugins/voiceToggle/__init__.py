# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/gpl-2.0.html>.

import addonHandler
import globalPluginHandler
import scriptHandler
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
		config.post_configProfileSwitch.register(self.app.handleProfileSwitch)

	def terminate(self):
		self.app.terminate()

	def __terminate__(self):
		self.terminate()
		super(GlobalPlugin, self).__terminate__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(OptionsPanel)

	@scriptHandler.script(
		gesture="kb:NVDA+Alt+V",
		# Translators: Gesture description for the Input gestures settings dialog
		description=_("Toggles to the next voice."),
	)
	def script_toggleVoice(self, gesture):
		self.app.toggleVoice()
