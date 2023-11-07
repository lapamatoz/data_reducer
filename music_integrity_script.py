# This code requires ffmpeg installed
import subprocess
from os.path import exists
import os, time

# This code "block" is for the directories where music files are read. There can be multiple directories in an array
from tkinter import filedialog
import tkinter as tk
root = tk.Tk()
root.withdraw()
rootdir = filedialog.askdirectory()
rootdirs = [rootdir]

# Directory 'tmp_dir' is where all the databases and a converted music file are put
#tmp_dir = '/home/lowpaw/Downloads/musaa'
#tmp_dir = '/storage/emulated/0/Download/musicscript'
#tmp_dir = os.getcwd()
tmp_dir = os.path.dirname(os.path.realpath(__file__))

#tmp_dir = 'C:\\Users\\lapam\\Nextcloud\\Dokumentit\\Koodausprojektit\\Data reducer\\music'
#rootdirs = ['/storage/emulated/0/Levyrip', '/storage/emulated/0/Download', '/storage/emulated/0/Musiikki']
max_handled_files = 500

def verify_integrity(full_name, tmp_dir):
  full_tmp = os.path.join(tmp_dir, 'tmp.mp3')
  if exists(full_tmp): # remove tmp converted file
    os.remove(full_tmp)
  s = ['ffmpeg', '-v', 'error', '-i', full_name, full_tmp] # full directories are mandatory
  res = subprocess.run(s, capture_output=True, text=True)
  res_str = res.stderr
  if res_str != '':
    return False
  else:
    # Here the conversion was successful
    # Just to be sure, we still verify the lengths of the two files
    return verify_lengths(full_name, full_tmp, tmp_dir)


def get_length(file_name, tmp_dir):
  s = ['ffmpeg', '-i', file_name]
  ffmpeg_outfile = os.path.join(tmp_dir, "ffmpeg_out.txt")
  with open(ffmpeg_outfile, 'w') as log: # no other way apparently :D wtf!
    ffmpeg_cmd = subprocess.run(s, stdout=log, stderr=log)
  fo = open(ffmpeg_outfile, 'r', errors="ignore")
  ffmpeg_output = fo.read()
  fo.close()
  ffmpeg_output = ffmpeg_output.split('Duration: ')[-1].split(', ')[0]
  # Output in milliseconds
  return 60*60*100*float(ffmpeg_output[0:2]) + 60*100*float(ffmpeg_output[3:5]) + 100*float(ffmpeg_output[6:8]) + float(ffmpeg_output[9:11])
  

def verify_lengths(file1, file2, tmp_dir):
  return abs(get_length(file1, tmp_dir) - get_length(file2, tmp_dir)) < 50.0 # 50 ms treshold
  

def is_music_file(file_dir):
  formats = ['.mp3', '.flac', '.wav', '.MP3', '.FLAC', '.WAV', '.Mp3', '.Flac', '.Wav']
  for f in formats:
    if f in file_dir:
      return True
  return False

print('got this far')
time.sleep(1)

database_dir = os.path.join(tmp_dir, 'music_integrity_database.txt')
error_log_dir = os.path.join(tmp_dir, 'music_integrity_errors.txt')

if exists(database_dir):
  fo = open(database_dir, 'r')
  database = fo.read()
  fo.close()
else:
  fo = open(database_dir, 'w')
  fo.close()
  database = ''


if not exists(error_log_dir):
  fo = open(error_log_dir, 'w')
  fo.close()


already_checked_files = database.split('\n')

#print(already_checked_files)
#exit()

handled_files = 0

print('got until loop')
time.sleep(1)

for rootdir in rootdirs:
  for subdir, dirs, files in os.walk(rootdir):
    for file_name in files:
      full_path = os.path.join(subdir, file_name)
      
      if is_music_file(file_name) and (not full_path in already_checked_files) and (full_path != os.path.join(tmp_dir, 'tmp.mp3')):
      
        if verify_integrity(full_path, tmp_dir):
          print(full_path + ' is OK')
        else:
          print(full_path + ' is NOT OK !!')
          # Add checked entry to error database
          fo = open(error_log_dir, 'a')
          fo.write("\n"+full_path)
          fo.close()
          
        # Add checked entry to database
        fo = open(database_dir, 'a')
        fo.write("\n"+full_path)
        fo.close()
        
        handled_files = handled_files + 1
      
      if handled_files >= max_handled_files:
        break
    if handled_files >= max_handled_files:
      break
  if handled_files >= max_handled_files:
    break

if exists(os.path.join(tmp_dir, 'tmp.mp3')): # remove tmp converted file
  os.remove(os.path.join(tmp_dir, 'tmp.mp3'))

#print('Done!')
input("Done! Press Enter to exit")