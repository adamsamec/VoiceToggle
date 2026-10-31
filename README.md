# VoiceToggle

## Introduction

The VoiceToggle add-on for NVDA screen reader allows you to preconfigure an arbitrary number of voices in its settings , so that you can later quickly switch between those voices in circle anytime in forward direction using the simple NVDA + Control + L keyboard shortcut, or in the reverse direction using NVDA + Control + Shift + L. Alternatively, a preconfigured voice can also be selected and switched to from a list using the NVDA + Alt + V shortcut.

## Example usage

Let's say you speak English and French, then you can add two voices in the VoiceToggle settings as described below, one with English and the other with French pronunciation. Anytime later you can switch between those two voices using only the NVDA + Control + L simple and comfortable keyboard shortcut instead of messing with the NVDA synth settings ring, NVDA synthesizer selection dialog, or with the speech category of the NVDA settings dialog.

## Configuring the voices

The voices to switch between using VoiceToggle can be preconfigured in the VoiceToggle settings by following these steps:

1. PressNVDA + N to open the NVDA menu.
2. Choose the "Preferences" submenu.
3. Choose the "Settings" menu item.
4. Navigate to the "VoiceToggle" category. The VoiceToggle property page opens, and the voices list will be populated with only the current voice.
5. TO add another voice to the list, open the dialog for adding a new voice using the "Add voice" button.
6. Using the first combo box, Select the desired synthesizer first, then using the second combo box, select the synthesizer's desired voice which you want to add, and press the "Add" button. The just added voice will appear in the voices list after the currently selected item in the list.
7. Don't forgot to save the settings just made by pressing the "OK" or "Apply" button at the end of the NVDA settings dialog.

## Other settings

You can control whether changes of the current voice using the synth settings ring, select synthesizer dialog, or via the speech category of the NVDA settings dialog also accordingly update the voices configured in the VoiceToggle settings. This can be controlled in the VoiceToggle settings using the "Update voice when NVDA's own speech settings change" checkbox.

## Remembering voices for individual applications

Let's say you want to browse the web in English, but want to make notes and all other work in French. Then you can have last used voice remembered in certain applications. For example, when you switch to Google Chrome, the voice automatically switches to the last used voice in that application, perhaps English. Then when you go back to another application, for example to Microsoft Word to make notes in French, the voice switches back to that default French voice. This is enabled thanks to the NVDA configuration profiles feature.

TO configure certain application so that it remembers the last used voice, follow these steps:

1. Switch to that application, for example to Google Chrome.
2. PressNVDA + N to open the NVDA menu.
3. Choose the "Configuration profiles" menu item.
4. Press the "New" button.
5. "Navigate to the radio button labelled as "Manual activation" under the "Use this profile for" grouping, and switch it to "Current application" using the Down arrow key.
6. Confirm the creation of a new configuration profile using the "OK" button.

## Changing the voice toggle shortcuts

The default NVDA + Control + L and NVDA + Control + Shift + L keyboard shortcuts for switching to the next or previous voice, respectively, as well as NVDA + Alt + V for showing the list of configured voices can be changed to another shortcuts using the "Input gestures" dialog as follows:

1. PressNVDA + N to open the NVDA menu.
2. Choose the "Preferences" submenu.
3. Choose the "Input gestures" menu item.
4. Type "voice" into the "Filter by" edit field.
5. In the tree, under the "Miscellaneous" category, navigate to the "Switches to the next voice", "Switches to the previous voice" or "Shows the Select a voice dialog" item depending on which shortcut you want to change.
6. Activate the "Add" button, then press the desired keyboard shortcut, and confirm with Enter.
7. Confirm the change using the "OK" button.

## Download

VoiceToggle for NVDA is available thrugh NVDA Add-on Store, or can be [downloaded here][VoiceToggle-download].

## Changelog

[The VoiceToggle changelog can be viewed here][changelog].

## Contact and feedback

If you have suggestions for VoiceToggle improvement, problems with its functionality or other comments, you can drop me an email to [adam.samec@gmail.com](mailto:adam.samec@gmail.com)

## License

VoiceToggle is available under the GNU General Public License version 2.0.

[VoiceToggle-download]: https://files.adamsamec.cz/apps/nvda/VoiceToggle.nvda-addon
[VoiceToggle-download-nvda-2023-1]: https://files.adamsamec.cz/apps/nvda/VoiceToggle-1.4.1.nvda-addon
[changelog]: https://github.com/adamsamec/VoiceToggle/blob/main/Changelog.md
