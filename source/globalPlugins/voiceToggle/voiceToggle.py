# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/>.

from synthDriverHandler import getSynth, setSynth, getSynthList, getSynthInstance, synthDoneSpeaking
from synthDrivers.silence import SynthDriver as SilenceSynthDriver
import config
import ui

import json
import os
import shutil
from urllib.request import urlopen, urlretrieve, URLError

# Constants
APP_VERSION = "1.3.1"
UPDATE_API_URL = "http://api.adamsamec.cz/nvda/VoiceToggle/Update.json"
TEMP_DIR = "..\\temp\\"

SILENCE_VOICE_NAME = _("Silence")
ONECORE_SYNTH_ID = "oneCore"

NORMAL_PROFILE_NAME = "[normal]"
CONFIG_SPEC = {
	"voiceSettings": "string_list(default=list())",
	"profilesVoiceSettingsIndeces": "string(default='{}')",
	"checkUpdateOnStart": "boolean(default=True)",
}
SAVED_PARAMS = ["volume", "rate", "pitch"]

class VoiceToggle:

	def __init__(self):
		config.conf.spec["VoiceToggle"] = CONFIG_SPEC

		currentDir = os.path.dirname(os.path.realpath(__file__))
		self.tempDirPath = os.path.join(currentDir, TEMP_DIR)
		self.isVoiceSettingsModified = False
		self.currentProfileName = NORMAL_PROFILE_NAME
		self.synthsInstances = None

		self.loadSettingsFromConfig()
		self.addDefaultVoiceSetting()
		self.alignCurrentVoiceSettingsIndex()
		self.checkForUpdateOnStart()

		synthDoneSpeaking.register(self.handleDoneSpeaking)

	@property
	def currentVoiceSettingsIndex(self):
		return self.profilesVoiceSettingsIndeces[self.currentProfileName]

	@currentVoiceSettingsIndex.setter
	def currentVoiceSettingsIndex(self, value):
		self.profilesVoiceSettingsIndeces[self.currentProfileName] = value

	def handleDoneSpeaking(self):
		newProfileName = config.conf.profiles[-1].name
		if not newProfileName:
			newProfileName = NORMAL_PROFILE_NAME
		if not (newProfileName in self.profilesVoiceSettingsIndeces):
			self.profilesVoiceSettingsIndeces[newProfileName] = self.currentVoiceSettingsIndex
		self.currentProfileName = newProfileName
		self.alignCurrentVoiceSettingsIndex()
		self.updateVoiceSetting()

	def alignCurrentVoiceSettingsIndex(self):
		if len(self.voiceSettings) == 0:
			return

		# This is an imperfect fix for cases when after switching to another profile or starting NVDA, the current synth and voice does not match the current voice setting
		synth = getSynth()
		currentVoiceSetting = self.voiceSettings[self.currentVoiceSettingsIndex]
		if currentVoiceSetting["synthId"] != synth.name or currentVoiceSetting["voiceId"] != synth.voice:
			for index, voiceSetting in enumerate(self.voiceSettings):
				if voiceSetting["synthId"] == synth.name and voiceSetting["voiceId"] == synth.voice:
					self.currentVoiceSettingsIndex = index
					break

	def getSynthsInstances(self):
		if self.synthsInstances == None:
			self.preloadSynthInstances()
		return self.synthsInstances

	def preloadSynthInstances(self):
		origSynthId = getSynth().name
		self.synthsInstances = []
		synthsInfos = getSynthList()
		for synthInfo in synthsInfos:
			synthId = synthInfo[0]
			isSilence = synthId == SilenceSynthDriver.name
			synthName = SILENCE_VOICE_NAME if isSilence else synthInfo[1]
			
			# setSynth("oneCore") throws strange error, so skip it
			if synthId == ONECORE_SYNTH_ID:
				continue

			try:
				instance = None if isSilence else getSynthInstance(synthId)
				self.synthsInstances.append({
					"id": synthId,
					"name": synthName,
					"instance": instance
				})
			except:
				pass

		# Resetting synth fixes the bug of broken ring after calling getSynthInstance()
		setSynth(origSynthId)

	def loadSettingsFromConfig(self):
		self.voiceSettings = [json.loads(voiceSetting) for voiceSetting in self.getConfig("voiceSettings")]
		self.profilesVoiceSettingsIndeces = json.loads(self.getConfig("profilesVoiceSettingsIndeces"))
		self.isCheckUpdateOnStart = self.getConfig("checkUpdateOnStart")
		voiceSettingsLength = len(self.voiceSettings)
		if not (NORMAL_PROFILE_NAME in self.profilesVoiceSettingsIndeces):
			if voiceSettingsLength > 0:
				self.profilesVoiceSettingsIndeces[NORMAL_PROFILE_NAME] = 0
			else:
				self.profilesVoiceSettingsIndeces[NORMAL_PROFILE_NAME] = -1
		if voiceSettingsLength == 0:
			for profileName in self.profilesVoiceSettingsIndeces:
				self.profilesVoiceSettingsIndeces[profileName] = -1

	def saveSettingsTOConfig(self):
		voiceSettingsJson = [json.dumps(voiceSetting) for voiceSetting in self.voiceSettings] 
		self.setConfig("voiceSettings", voiceSettingsJson)
		self.setConfig("profilesVoiceSettingsIndeces", json.dumps(self.profilesVoiceSettingsIndeces))
		self.setConfig("checkUpdateOnStart", self.isCheckUpdateOnStart)

	def checkForUpdateOnStart(self):
		if self.isCheckUpdateOnStart:
			update = self.checkForUpdate()
			if isinstance(update, dict):
				updateAvailableDialog = UpdateAvailableDialog(self, update, displayCheckOnStartCheckbox=True)
				updateAvailableDialog.Show()
				updateAvailableDialog.Raise()

	def checkForUpdate(self):
		try:
			response = urlopen(UPDATE_API_URL)
			update = json.loads(response.read())

			# Compare the latest version with the current version
			if self.isUpdateAvailable(update["version"]):
				return update

			# True means we are up to date
			return True
		except URLError:
			pass
			
		# False means a request error occurred, such as no Internet
		return False

	def addDefaultVoiceSetting(self):
		# Create and add the default voice setting if does not exist, but only for other than OneCore synths
		if len(self.voiceSettings) == 0:
			self.currentVoiceSettingsIndex = 0
			voiceSetting = self.getFreshVoiceSetting()
			if voiceSetting != None:
				self.voiceSettings.append(voiceSetting)

	def getVoiceSettings(self):
		return self.voiceSettings.copy()

	def setVoiceSettings(self, settings):
		self.voiceSettings = settings.copy()
		self.saveSettingsTOConfig()

	def markVoiceSettingsAsModified(self):
		self.isVoiceSettingsModified = True

	def toggleVoice(self):
		if len(self.voiceSettings) == 0:
			return
		nextIndex = self.getNextVoiceSettingsIndex(self.currentVoiceSettingsIndex)
		newIndex = self.changeVoice(nextIndex)
		self.currentVoiceSettingsIndex = newIndex

	def getNextVoiceSettingsIndex(self, index):
		voiceSettingsLength = len(self.voiceSettings)
		if voiceSettingsLength == 0:
			return -1
		
		# If index is out of list bounds and list is not empty, return zero
		if index < 0 or index >= voiceSettingsLength:
			return 0
		newIndex = (index + 1) % voiceSettingsLength
		return newIndex

	def changeVoice(self, newIndex, announceChange=True):
		voiceSettingsLength = len(self.voiceSettings)
		if (newIndex >= voiceSettingsLength) or (newIndex < 0):
			if voiceSettingsLength > 0:
				return 0
			else:
				return -1
		
		# Determine the next voice setting
		newVoiceSetting = self.voiceSettings[newIndex]

		# Delete all invalid voice settings starting from the new index, and update the new index if necessary
		newIndex = self.deleteInvalidVoiceSettings(startIndex=newIndex, dontChangeVoice=True)
		newVoiceSetting = self.voiceSettings[newIndex]

		synth = getSynth()

		# To prevent mismatch, don't update current synth, voice and speech params if voice settings have been modified in NVDA settings, or if changed voice settings due to invalidation
		currentVoiceSetting = None if self.isVoiceSettingsModified else self.updateVoiceSetting()
		
		# Only apply new synth if voice settings have been modified in add-on settings, if changed from previous one, or if is OneCore voice and new is not
		if (currentVoiceSetting == None) or (newVoiceSetting["synthId"] != currentVoiceSetting["synthId"]) or (newVoiceSetting["synthId"] != ONECORE_SYNTH_ID and synth.name == ONECORE_SYNTH_ID):
			if newVoiceSetting["synthId"] == SilenceSynthDriver.name:
				setSynth(None)
			else:
				setSynth(newVoiceSetting["synthId"])
				synth = getSynth()
		
		# Apply new voice setting
		if newVoiceSetting["synthId"] != SilenceSynthDriver.name:
			synth.voice = newVoiceSetting["voiceId"]
			for param in SAVED_PARAMS:
				if param in newVoiceSetting:
					setattr(synth, param, newVoiceSetting[param])
			if synth != None:
				synth.saveSettings()
		if announceChange:
			ui.message(newVoiceSetting["voiceName"])
		self.isVoiceSettingsModified = False
		return newIndex

	def deleteInvalidVoiceSettings(self, startIndex=0, dontChangeVoice=False):
		newValidIndex = startIndex
		doChangeVoice = False

		# Start deleting from start index
		index = self.findNextInvalid(startIndex)

		voiceSettingsLength = len(self.voiceSettings)
		while voiceSettingsLength > 0 and index >= 0:
			del self.voiceSettings[index]
			voiceSettingsLength = len(self.voiceSettings)

			# If some setting before the current one has been deleted, shift the current index to the previous index and change the voice
			if index < self.currentVoiceSettingsIndex:
				self.currentVoiceSettingsIndex -= 1
				doChangeVoice = True

			# If setting at the same index as the current setting has been deleted, change the voice
			elif index == self.currentVoiceSettingsIndex:
				doChangeVoice = True
				
			# If some setting before the start index has been deleted, shift the new valid index to the previous index
			if index < startIndex:
				newValidIndex -= 1

			index = self.findNextInvalid(index)

		# Check if list has been deleted entirely or was originally empty
		if voiceSettingsLength == 0:
			self.currentVoiceSettingsIndex = -1
			return -1
		
		if doChangeVoice and not dontChangeVoice:
			self.isVoiceSettingsModified = True
			self.changeVoice(self.currentVoiceSettingsIndex, announceChange=False)

		return newValidIndex

	def findNextInvalid(self, startIndex):
		if len(self.voiceSettings) == 0:
			return -1

		# If start index is out of list bounds, start at zero
		if startIndex < 0 or startIndex >= len(self.voiceSettings):
			startIndex = 0

		index = startIndex
		while index >= 0 and self.synthAndVoiceExist(self.voiceSettings[index]):
			# If list is empty, return not found
			if len(self.voiceSettings) == 0:
				return -1
			index = self.getNextVoiceSettingsIndex(index)

			# If we are back on start, we have traversed entire list, so return not found
			if index == startIndex:
				return -1
		return index

	def synthAndVoiceExist(self, voiceSetting):
		synthExists = False
		voiceExists = False
		synthInstances = self.getSynthsInstances()
		for instance in synthInstances:
			if instance["id"] == voiceSetting["synthId"]:
				synthExists = True
				for voiceId in instance["instance"].availableVoices:
					if voiceId == voiceSetting["voiceId"]:
						voiceExists = True
						break
				else:
					continue
				break # Executed only if inner loop broke
		return synthExists and voiceExists

	def updateVoiceSetting(self):
		if self.currentVoiceSettingsIndex < 0 or len(self.voiceSettings) <= self.currentVoiceSettingsIndex:
			return None
		currentVoiceSetting = self.voiceSettings[self.currentVoiceSettingsIndex]
		synth = getSynth()
		isSilenceFresh = synth == None
		if not isSilenceFresh:
			for param in SAVED_PARAMS:
				currentVoiceSetting[param] = getattr(synth, param)

		# Determine and update fresh synth and voice names only when synth or voice ID changed
		isChangeToSilence = isSilenceFresh and currentVoiceSetting["synthId"] != SilenceSynthDriver.name
		isSynthOrVoiceChange = not isSilenceFresh and (synth.name != currentVoiceSetting["synthId"] or synth.voice != currentVoiceSetting["voiceId"])
		if isChangeToSilence or isSynthOrVoiceChange:
			freshVoiceSetting = self.getFreshVoiceSetting()
			self.voiceSettings[self.currentVoiceSettingsIndex] = {**currentVoiceSetting, **freshVoiceSetting}
		return currentVoiceSetting

	def getFreshVoiceSetting(self):
		synth = getSynth()
		if synth.name == ONECORE_SYNTH_ID:
			if len(self.voiceSettings) == 0:
				return None
			currentVoiceSetting = self.voiceSettings[self.currentVoiceSettingsIndex]
			synthId = currentVoiceSetting["synthId"]
		else:
			currentVoiceSetting = None
			synthId = SilenceSynthDriver.name if synth == None else synth.name
		synthInstance = next(instance for instance in self.getSynthsInstances() if instance["id"] == synthId)
		if synthId == SilenceSynthDriver.name:
			voiceId = SilenceSynthDriver.name
			voiceName = SILENCE_VOICE_NAME
		else:
			if synth.name == ONECORE_SYNTH_ID:
				voiceId = currentVoiceSetting["voiceId"]
			else:
				voiceId = synth.voice
			voices = synthInstance["instance"].availableVoices
			voiceName = next(voices[id].displayName for id in voices if id == voiceId)
		voiceSetting = {
			"synthId": synthId,
			"synthName": synthInstance["name"],
			"voiceId": voiceId,
			"voiceName": voiceName
		}
		return voiceSetting

	def getConfig(self, key):
		return config.conf["VoiceToggle"][key]

	def setConfig(self, key, value):
		config.conf["VoiceToggle"][key] = value

	def isUpdateAvailable(self, latestVersion):
		current = [int(part) for part in APP_VERSION.split(".")]
		latest = [int(part) for part in latestVersion.split(".")]
		isAvailable = latest[0] > current[0] or latest[1] > current[1] or latest[2] > current[2]
		return isAvailable

	def downloadAndRunUpdate(self, url):
		try:
			response = urlopen(url)

			# Get the filename from URL after redirect
			newFilename = os.path.basename(response.geturl())

			response = urlretrieve(url)

			# Copy the downloaded file from download directory to plugin temp directory
			downloadPath = response[0]
			newPath = os.path.join(self.tempDirPath, newFilename)
			shutil.copy2(downloadPath, newPath)
			
			# Run the file
			os.startfile(newPath)
			return True
		except Exception:
			pass
		return False

	def deleteTempFiles(self):
		for filename in os.listdir(self.tempDirPath):
			path = os.path.join(self.tempDirPath, filename)
			try:
				if os.path.isfile(path) or os.path.islink(path):
					os.unlink(path)
				elif os.path.isdir(path):
					shutil.rmtree(path)
					return True
			except Exception:
				pass
		return False

	def terminate(self):
		# Save current synth, voice and speech params before terminating
		# if len(self.voiceSettings) > 0 and not self.isVoiceSettingsModified:
			# self.updateVoiceSetting()
			
		self.saveSettingsTOConfig()
		self.deleteTempFiles()
