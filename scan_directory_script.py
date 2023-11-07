import datareducer
from os.path import exists
from tkinter import filedialog
import tkinter as tk
from pandas import ExcelWriter # just checking if this exists
import os

excel_dir = os.path.dirname(os.path.realpath(__file__))

root = tk.Tk()
root.withdraw()

input("Press Enter and choose a directory to reduce")
rootdir = filedialog.askdirectory()

blacklist_boolean = input("Do you want to enter a blacklist file? 1: yes, 2: no: ")
blacklist_boolean = (blacklist_boolean == '1')

if blacklist_boolean:
    blacklist_name = filedialog.askopenfilename()
    warning_message = input("This program deletes files PERMANENTLY. Files do NOT go into the recycle bin. 1: continue, 2: exit program: ")
    if warning_message != '1':
        print("Exiting...")
        time.sleep(1.5)
        exit()

rescan_is_required = True

# We scan the directory and delete duplicates, until no duplicates are deleted
# If blacklist is not provided, only one scan is performed
while rescan_is_required:
    datareducer.find_files_and_folders.execute(rootdir, excel_dir)
    if blacklist_boolean:
        number_of_deleted_files = datareducer.delete_files.delete_duplicates_with_rules(blacklist_name, excel_dir)
        rescan_is_required = (number_of_deleted_files != 0)
    else:
        rescan_is_required = False

input("Press Enter to exit")
