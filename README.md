# Data Reducer

This is a collection of scripts in Python. It has been developed on a Windows machine, but should work on any platform. The program ```scan_directory.py``` asks for a directory and outputs a summary in csv-tables:

* 200 largest file duplicates (uses file size as well as md5 hash to verify the duplicates)
* 200 largest files
* 200 folders with most files and sub-folders
* Potential temporary files and folders
* Empty files and folders

The idea is that the user first handles the listed 200 files and re-runs the program until there is no redundant files or folders. The 200 file limit makes the program quite a bit faster, and provides the user with a lot of data anyway.

The csv-files can be opened in Excel and the user can mark files and folders for deletion. On Windows, the individual files and folders can be opened quickly by copy pasting the file/folder path from Excel to File Explorer. Files and folders with a lowercase ```x``` in the *Delete*-column are to be deleted. The deletion process is performed with script ```delete_files.py```.

In addition, the script supports a *blacklist* for duplicates. A file is considered blacklisted if an item on the blacklist is a sub-string of the file path. Also, there are different *blacklist levels*, e.g., the level is two, if two blacklist items are substrings of the file path. A duplicate file with a higher blacklist level will be deleted. If two duplicate files have same blacklist level, neither will be deleted. With blacklist rules, there is no possibility of data loss, i.e., the blacklist process will always keep at least one instance of each unique file. The program checks the existance of the files just before each duplicate deletion.

Developer info and requirements
* Only required package is Pandas. All other packages are included in Python 3.12.
* The md5 hashing is now done in 1MB chunks. The mistake was noticed when trying to hash a 10 GB file...

## Music integrity checker
This script finds music files in a directory and checks the integrity of them in case of... a download error or other kind of data loss. It works by encoding each file to mp3 with ```ffmpeg```: if the files have same duration, the file is considered to be intact. If the ```ffmpeg``` fails, or the duration does not match, the file is flagged corrupted. This script will not delete anything, it is only a file scanner. The script is quite slow, so only 500 music files are processed at each run, and a database is updated. In the next run, the script processes the next 500 files, etc. The output is a ```txt```-file with path to corrupted music files.

With minor modifications, the script can be used on Android (Termux with ```ffmpeg``` installed). The modification is with the ```tkinter``` block: one should hard code the directory (or directories) instead of the user prompt with ```tkinter```.
