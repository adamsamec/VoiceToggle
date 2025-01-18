# Copyright 2025 Adam Samec <adam.samec@gmail.com>
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2). see <https://www.gnu.org/licenses/gpl-2.0.html>.

import addonHandler
from synthDriverHandler import getSynth, setSynth, getSynthList, getSynthInstance
from synthDrivers.silence import SynthDriver as SilenceSynthDriver
import config
import ui

import json

import globalPlugins.voiceToggle.consts as consts

addonHandler.initTranslation()

class VoiceToggle:

	def __init__(self):
		config.conf.spec["VoiceToggle"] = consts.CONFIG_SPEC

		self.isVoiceSettingsModified = False
		self.currentProfileName = consts.NORMAL_PROFILE_NAME
		self.synthsWithVoices = []

		self.loadSettingsFromConfig()
		self.addDefaultVoiceSetting()
		self.alignCurrentVoiceSettingsIndex()

	@property
	def currentVoiceSettingsIndex(self):
		return self.profilesVoiceSettingsIndices[self.currentProfileName]

	@currentVoiceSettingsIndex.setter
	def currentVoiceSettingsIndex(self, value):
		self.profilesVoiceSettingsIndices[self.currentProfileName] = value

	def handleDoneSpeaking(self):
		newProfileName = config.conf.profiles[-1].name
		if not newProfileName:
			newProfileName = consts.NORMAL_PROFILE_NAME
		if not (newProfileName in self.profilesVoiceSettingsIndices):
			self.profilesVoiceSettingsIndices[newProfileName] = self.currentVoiceSettingsIndex
		self.currentProfileName = newProfileName
		self.alignCurrentVoiceSettingsIndex()
		self.updateVoiceSetting()

	def cleanUpVoiceSettings(self):
		self.updateSynthsWithVoices()
		self.currentVoiceSettingsIndex = self.deleteInvalidVoiceSettings(startIndex=self.currentVoiceSettingsIndex)
		self.addDefaultVoiceSetting()
		self.alignCurrentVoiceSettingsIndex()

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

		# If we deleted voice settings at the start index and after it, move index to 0
		if newValidIndex >= voiceSettingsLength:
			newValidIndex = 0
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
		for synthWithVoices in self.synthsWithVoices:
			synthId = voiceSetting["synthId"]
			if synthWithVoices["id"] == synthId:
				synthExists = True
				if synthId == SilenceSynthDriver.name:
					voiceExists = True
					break
				voices = self.getVoicesForSynth(synthId)
				if voices == None:
					return False
				for voice in voices:
					if voice["id"] == voiceSetting["voiceId"]:
						voiceExists = True
						break
				else:
					continue
				break # Executed only if inner loop broke
		return synthExists and voiceExists

	def updateSynthsWithVoices(self):
		newSynthsWithVoices = []
		synthsInfos = getSynthList()
		for synthInfo in synthsInfos:
			synthId = synthInfo[0]
			try:
				# Try finding existing synth with voices dict and appending it
				existingSynthWithVoices = next(synthWithVoices for synthWithVoices in self.synthsWithVoices if synthWithVoices["id"] == synthId)
				newSynthsWithVoices.append(existingSynthWithVoices)
			except StopIteration:
				# If not already exists, append the new synth with voices dict
				isSilence = synthId == SilenceSynthDriver.name
				synthName = consts.SILENCE_VOICE_NAME if isSilence else synthInfo[1]
				newSynthsWithVoices.append({
					"id": synthId,
					"name": synthName,
					"voices": None
				})
		self.synthsWithVoices = newSynthsWithVoices

	def getSynthsWithVoices(self):
		return self.synthsWithVoices.copy()

	def getVoicesForSynth(self, synthId):
		if synthId == SilenceSynthDriver.name:
			return None
		for synthWithVoices in self.synthsWithVoices:
			if synthWithVoices["id"] == synthId:
				if synthWithVoices["voices"] == None:
					synth = getSynth()
					if synth.name== synthId:
						voices = synth.availableVoices
						synthWithVoices["voices"] = [{"id": id, "name": voices[id].displayName} for id in voices]
					else:
						try:
							instance = getSynthInstance(synthId)
							voices = instance.availableVoices
							synthWithVoices["voices"] = [{"id": id, "name": voices[id].displayName} for id in voices]
							instance.terminate()
							del instance
						except:
							return None
				return synthWithVoices["voices"]
		return None

	def getSynthNameById(self, synthId):
		try:
			synthName = next(synthWithVoices["name"] for synthWithVoices in self.synthsWithVoices if synthWithVoices["id"] == synthId)
			return synthName
		except StopIteration:
			return None

	def getVoiceNameById(self, synthId, voiceId):
		voices = self.getVoicesForSynth(synthId)
		if voices == None:
			return None
		try:
			voiceName = next(voice["name"] for voice in voices if voice["id"] == voiceId)
			return voiceName
		except StopIteration:
			return None

	def alignCurrentVoiceSettingsIndex(self):
		voiceSettingsLength = len(self.voiceSettings)
		if voiceSettingsLength == 0 or self.currentVoiceSettingsIndex < -1 or self.currentVoiceSettingsIndex >= voiceSettingsLength:
			return

		# This is an imperfect fix for cases when the current synth and voice does not match the current voice setting, e.g., after changing synth using NVDA settings or voice using speech param ring
		synth = getSynth()
		currentVoiceSetting = self.voiceSettings[self.currentVoiceSettingsIndex]
		if currentVoiceSetting["synthId"] != synth.name or currentVoiceSetting["voiceId"] != synth.voice:
			for index, voiceSetting in enumerate(self.voiceSettings):
				if voiceSetting["synthId"] == synth.name and voiceSetting["voiceId"] == synth.voice:
					self.currentVoiceSettingsIndex = index
					break

	def loadSettingsFromConfig(self):
		self.voiceSettings = [json.loads(voiceSetting) for voiceSetting in self.getConfig("voiceSettings")]
		self.profilesVoiceSettingsIndices = json.loads(self.getConfig("profilesVoiceSettingsIndices"))
		
		# Create index for naormal profile if not exists
		voiceSettingsLength = len(self.voiceSettings)
		if not (consts.NORMAL_PROFILE_NAME in self.profilesVoiceSettingsIndices):
			if voiceSettingsLength > 0:
				self.profilesVoiceSettingsIndices[consts.NORMAL_PROFILE_NAME] = 0
			else:
				self.profilesVoiceSettingsIndices[consts.NORMAL_PROFILE_NAME] = -1

		if voiceSettingsLength == 0:
			# Set negative index for all profiles if there are no voice settings
			for profileName in self.profilesVoiceSettingsIndices:
				self.profilesVoiceSettingsIndices[profileName] = -1
		else:
			# Set index to 0 if index is out of voice settings bounds for each profile
			for profileName in self.profilesVoiceSettingsIndices:
				if self.profilesVoiceSettingsIndices[profileName] < 0 or self.profilesVoiceSettingsIndices[profileName] >= len(self.voiceSettings):
					self.profilesVoiceSettingsIndices[profileName] = 0

	def saveSettingsTOConfig(self):
		voiceSettingsJson = [json.dumps(voiceSetting) for voiceSetting in self.voiceSettings]
		self.setConfig("voiceSettings", voiceSettingsJson)
		self.setConfig("profilesVoiceSettingsIndices", json.dumps(self.profilesVoiceSettingsIndices))

	def addDefaultVoiceSetting(self):
		# Create and add the default voice setting if does not exist
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
		self.updateSynthsWithVoices()
		newIndex = self.deleteInvalidVoiceSettings(startIndex=newIndex, dontChangeVoice=True)
		self.addDefaultVoiceSetting()
		voiceSettingsLength = len(self.voiceSettings)
		if voiceSettingsLength == 0:
			# If after deleting all invalid voice settings there were no voice settings and we did not add a default one, return -1
			return -1
		elif newIndex == -1:
			# If after deleting all invalid voice settings there were no voice settings and we added a default one, set index to this default voice setting index
			newIndex = 0

		newVoiceSetting = self.voiceSettings[newIndex]

		synth = getSynth()

		# To prevent mismatch, don't update current synth, voice and speech params if voice settings have been modified in NVDA settings, or if changed voice settings due to invalidation
		if self.isVoiceSettingsModified:
			currentVoiceSetting = None
		else:
			self.alignCurrentVoiceSettingsIndex()
			currentVoiceSetting = self.updateVoiceSetting()
		
		# Only apply new synth if voice settings have been modified in add-on settings, or if changed from previous one
		if currentVoiceSetting == None or newVoiceSetting["synthId"] != synth.name:
			if newVoiceSetting["synthId"] == SilenceSynthDriver.name:
				setSynth(None)
			else:
				setSynth(newVoiceSetting["synthId"])
				synth = getSynth()
		
		# Apply new voice setting
		if newVoiceSetting["synthId"] != SilenceSynthDriver.name:
			synth.voice = newVoiceSetting["voiceId"]
			for param in consts.SAVED_PARAMS:
				if param in newVoiceSetting:
					setattr(synth, param, newVoiceSetting[param])
			if synth != None:
				synth.saveSettings()
		if announceChange and newVoiceSetting["synthId"] != SilenceSynthDriver.name:
			voiceName = self.getVoiceNameById(newVoiceSetting["synthId"], newVoiceSetting["voiceId"])
			ui.message(voiceName)
		self.isVoiceSettingsModified = False
		return newIndex

	def updateVoiceSetting(self):
		if self.currentVoiceSettingsIndex < 0 or len(self.voiceSettings) <= self.currentVoiceSettingsIndex:
			return None
		currentVoiceSetting = self.voiceSettings[self.currentVoiceSettingsIndex]
		synth = getSynth()
		isSilenceFresh = synth == None
		if not isSilenceFresh:
			for param in consts.SAVED_PARAMS:
				currentVoiceSetting[param] = getattr(synth, param)

		# Determine and update fresh synth and voice IDs and names only when synth or voice ID changed
		isChangeToSilence = isSilenceFresh and currentVoiceSetting["synthId"] != SilenceSynthDriver.name
		isSynthOrVoiceChange = not isSilenceFresh and (synth.name != currentVoiceSetting["synthId"] or synth.voice != currentVoiceSetting["voiceId"])
		if isChangeToSilence or isSynthOrVoiceChange:
			freshVoiceSetting = self.getFreshVoiceSetting()
			self.voiceSettings[self.currentVoiceSettingsIndex] = {**currentVoiceSetting, **freshVoiceSetting}
		return currentVoiceSetting

	def getFreshVoiceSetting(self):
		synth = getSynth()
		if synth == None:
			synthId = SilenceSynthDriver.name
			voiceId = SilenceSynthDriver.name
		else:
			synthId = synth.name
			voiceId = synth.voice
		voiceSetting = {
			"synthId": synthId,
			"voiceId": voiceId,
		}
		return voiceSetting

	def getConfig(self, key):
		return config.conf["VoiceToggle"][key]

	def setConfig(self, key, value):
		config.conf["VoiceToggle"][key] = value

	def terminate(self):
		self.saveSettingsTOConfig()

# Create the app
voiceToggle = VoiceToggle()
