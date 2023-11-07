import datareducer
from tkinter import filedialog
import tkinter as tk
import time
import os

root = tk.Tk()
root.withdraw()

#input("Press Enter and choose folder where the csv results files are")
#excel_file_name = filedialog.askdirectory()
#excel_file_name = filedialog.askopenfilename()

excel_file_name = os.path.dirname(os.path.realpath(__file__)) # REALLY DIRECTORY

blacklist_boolean = input("Do you want to enter a blacklist file? 1: yes, 2: no: ")
blacklist_boolean = (blacklist_boolean == '1')

if blacklist_boolean:
    blacklist_name = filedialog.askopenfilename()

warning_message = input("This program deletes files PERMANENTLY. Files do NOT go into the recycle bin. 1: continue, 2: exit program: ")

if warning_message != '1':
    print("Exiting...")
    time.sleep(1.5)
    exit()

to_be_deleted = datareducer.delete_files.read_excel_and_find_items_marked_with_x(excel_file_name)
datareducer.delete_files.delete_items_marked_with_x(to_be_deleted)

if blacklist_boolean:
    datareducer.delete_files.delete_duplicates_with_rules(blacklist_name, excel_file_name)
    
input("Press Enter to exit")
