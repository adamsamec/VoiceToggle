# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/>.

import addonHandler
import globalPluginHandler
import scriptHandler
import gui

from .settingsDialogs import OptionsPanel
from .voiceToggle import voiceToggle

addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self):
		super(GlobalPlugin, self).__init__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(OptionsPanel)

	def terminate(self):
		voiceToggle.terminate()

	def __terminate__(self):
		super(GlobalPlugin, self).__terminate__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(OptionsPanel)

	@scriptHandler.script(
		gesture="kb:NVDA+Alt+V",
		description=_("Toggles to the next voice."),
	)
	def script_toggleVoice(self, gesture):
		voiceToggle.toggleVoice()
