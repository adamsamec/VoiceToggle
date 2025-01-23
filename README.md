# VoiceToggle

## Introduction

The VoiceToggle add-on for NVDA screen reader allows you to preconfigure an arbitrary number of voices in its settings , so that you can later toggle between those voices in circle anytime using the simple NVDA + Alt + V keyboard shortcut.

## Example usage

Let's say you speak English and French, then you can add two voices in the VoiceToggle settings as described below, one with English and the other with French pronunciation. Anytime later you can toggle between those two voices using only the NVDA + Alt + V simple and comfortable keyboard shortcut instead of messing with the NVDA synth settings ring, NVDA synthesizer selection dialog, or with the NVDA settings dialog in the Speech category.

## Configuring the voices

The voices to toggle between using VoiceToggle can be preconfigured by following these steps:

1. PressNVDA + N to open the NVDA menu.
2. Choose the "Preferences" submenu.
3. Choose the "Settings" menu item.
4. Navigate to the "VoiceToggle" category. The VoiceToggle property page opens, and the voices list will be populated with only the current voice.
5. TO add another voice to the list, open the "Add voice" dialog using the "Add voice" button.
6. Using the first combo box, Select the desired synthesizer first, then using the second combo box, select the synthesizer's desired voice which you want to add, and press the "Add" button. The just added voice will appear in the "Voices" list after the currently selected item in the list.
7. Don't forgot to save the settings made by pressing the "OK" or "Apply" button of the NVDA settings dialog.

## Remembering voices for individual applications

Let's say you want to browse the web in English, but want to make notes and all other work in French. Then you can have last used voice remembered by selected applications. For example, when you switch to Google Chrome, the voice automatically switches to the last used voice in that application, perhaps English. Then when you go back to another application, for example to Microsoft Word to make notes in French, the voice switches back to that default voice. This is enabled thanks to the NVDA configuration profiles feature.

TO configure certain application so that it remembers the last used voice, follow these steps:

1. Switch to that application, for example to Google Chrome.
2. PressNVDA + N to open the NVDA menu.
3. Choose the "Configuration profiles" menu item.
4. Press the "New" button.
5. "Navigate to the radio button labelled as "Manual activation" under the "Use this profile for" grouping, and switch it to "Current application" using the Down arrow key.
6. Confirm the changes using the "OK" button.

## Changing the voice toggle shortcut

The NVDA + Alt + V keyboard shortcut for voice toggling can be changed to another shortcut using the "Input gestures" dialog as follows:

1. PressNVDA + N to open the NVDA menu.
2. Choose the "Preferences" submenu.
3. Choose the "Input gestures" menu item.
4. Type "voice toggle" into the "Filter by" edit field, including the space between the two words.
5. In the tree, navigate to the "Toggles to the next voice" tree node under the "Miscellaneous" category.
6. Activate the "Add" button, then press the desired keyboard shortcut, and confirm with Enter.
7. Confirm the changes using the "OK" button.

## Download

VoiceToggle for NVDA is available thrugh NVDA Add-on Store, or can be [downloaded here][VoiceToggle-download].

## Changelog

[The changelog can be viewed here][changelog].

## Contact and feedback

If you have suggestions for VoiceToggle improvement, problems with its functionality or other comments, you can drop me an email to [adam.samec@gmail.com](mailto:adam.samec@gmail.com)

## Licence

VoiceToggle is available under the GNU General Public License version 2.

[VoiceToggle-download]: https://files.adamsamec.cz/apps/nvda/VoiceToggle.nvda-addon
[VoiceToggle-download-nvda-2023-1]: https://files.adamsamec.cz/apps/nvda/VoiceToggle-1.4.1.nvda-addon
[changelog]: https://github.com/adamsamec/VoiceToggle/blob/main/Changelog.md
