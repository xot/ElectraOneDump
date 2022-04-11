# ElectraOneDump

Ableton Live MIDI Remote Script to dump an ElectraOne JSON preset for the currently selected device

Dumps all the parameters in the currently selected device as an ElectraOne JSON preset in the user home directory, or in a sub-directory specified in the source. 


## Installation

Copy all Python files to your local Ableton MIDI Live Scripts folder (```~/Music/Ableton/User Library/Remote Scripts/``` on MacOS and
```~\Documents\Ableton\User Library\Remote Scripts``` on Windows) into a directory called ```ElectraOneDump````.

Edit the ```LOCALDIR``` constant in ```ElectraOneDump.py``` to change the default location where dumps are saved.

Add ElectraOneDump as a Control Surface in Live > Preferences > MIDI.

Any device selected (the 'Blue Hand') will automatically be dumped.

See ```~/Library/Preferences/Ableton/Live <version>/Log.txt``` for any error messages.
