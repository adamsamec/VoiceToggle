# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/>.

import addonHandler

addonHandler.initTranslation()

# Constants
UPDATE_API_URL = "http://api.adamsamec.cz/nvda/VoiceToggle/Update.json"
TEMP_DIR = "..\\..\\temp\\"

SILENCE_VOICE_NAME = _("Silence")

NORMAL_PROFILE_NAME = "[normal]"
CONFIG_SPEC = {
	"voiceSettings": "string_list(default=list())",
	"profilesVoiceSettingsIndices": "string(default='{}')",
	"checkUpdateOnStart": "boolean(default=True)",
}
SAVED_PARAMS = ["volume", "rate", "pitch"]
