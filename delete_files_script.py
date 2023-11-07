import datareducer
from tkinter import filedialog
import tkinter as tk
import time
import os

# Prepare file secection prompt
root = tk.Tk()
root.withdraw()

# Choose csv-directory, the folder where this script is
excel_dir = os.path.dirname(os.path.realpath(__file__))

# Prompt blacklist
blacklist_boolean = input("Do you want to enter a blacklist file? 1: yes, 2: no: ")
blacklist_boolean = (blacklist_boolean == '1')

if blacklist_boolean:
    blacklist_name = filedialog.askopenfilename()

warning_message = input("This program deletes files PERMANENTLY. Files do NOT go into the recycle bin. 1: continue, 2: exit program: ")

if warning_message != '1':
    print("Exiting...")
    time.sleep(1.5)
    exit()

# Read csv's and delete the items marked with 'x'
to_be_deleted = datareducer.delete_files.read_excel_and_find_items_marked_with_x(excel_dir)
datareducer.delete_files.delete_items_marked_with_x(to_be_deleted)

# Run blacklist delete script, if a blacklist is provided
if blacklist_boolean:
    datareducer.delete_files.delete_duplicates_with_rules(blacklist_name, excel_dir)
    
input("Press Enter to exit")
