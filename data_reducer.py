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
#input("Press Enter and choose a directory for the Excel result file")
#excel_dir = filedialog.askdirectory()
#excel_dir = rootdir

blacklist_boolean = input("Do you want to enter a blacklist file? 1: yes, 2: no: ")
blacklist_boolean = (blacklist_boolean == '1')

if blacklist_boolean:
    blacklist_name = filedialog.askopenfilename()
    warning_message = input("This program deletes files PERMANENTLY. Files do NOT go into the recycle bin. 1: continue, 2: exit program: ")
    if warning_message != '1':
        print("Exiting...")
        time.sleep(1.5)
        exit()

excel_file_name = 'datareducer.xlsx'
iterator = 1

if exists(excel_dir + '/' + excel_file_name):
    while exists(excel_dir + '/' + excel_file_name):
        excel_file_name = 'datareducer ({}).xlsx'.format(iterator)
        iterator = iterator + 1

deleted = 1

while deleted != 0:
    datareducer.find_files_and_folders.execute(rootdir, excel_dir, excel_file_name)
    if blacklist_boolean:
        deleted = datareducer.delete_files.delete_duplicates_with_rules(blacklist_name, excel_file_name)
    else:
        deleted = 0

input("Press Enter to exit")
