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
