import os, shutil
import pandas as pd
from os.path import exists
import os

def append_sheet_with_files_marked_delete(df, sheet_name, excel_dir):
    file_path = os.path.join(excel_dir, sheet_name + '.csv')
    if exists(file_path):
        sheet = pd.read_csv(file_path, sep=';')
        sheet = sheet[['Directory','Delete']]
        # Filter only the files and folders which are marked with 'x'
        sheet = sheet[sheet['Delete'] == 'x']
        return pd.concat([df, sheet])
    else:
        print('Could not find file "' + sheet_name + '.csv"')
        return df

def read_excel_and_find_items_marked_with_x(excel_dir):
    to_be_deleted = pd.DataFrame()
    to_be_deleted = append_sheet_with_files_marked_delete(to_be_deleted, 'DuplicateFiles', excel_dir)
    to_be_deleted = append_sheet_with_files_marked_delete(to_be_deleted, 'BadFiles', excel_dir)
    to_be_deleted = append_sheet_with_files_marked_delete(to_be_deleted, 'BadFolders', excel_dir)
    to_be_deleted = append_sheet_with_files_marked_delete(to_be_deleted, 'LargestFiles', excel_dir)
    to_be_deleted = append_sheet_with_files_marked_delete(to_be_deleted, 'LargestFolders', excel_dir)
    to_be_deleted = pd.unique(to_be_deleted['Directory'])
    to_be_deleted = list(to_be_deleted)
    #print(to_be_deleted)
    return to_be_deleted

def delete_items_marked_with_x(to_be_deleted):
    counter_file = 0
    counter_folder = 0
    for file in to_be_deleted:
        try:
            os.remove(file)
            counter_file = counter_file +1
        except:
            try:
                shutil.rmtree(file) # removes directory wth files inside
                counter_folder = counter_folder + 1
            except:
                print('Unable to remove file or folder: ' + file)
    print('Deleted ' + str(counter_file) + ' files marked with x')
    print('Deleted ' + str(counter_folder) + ' folders marked with x')
    return counter_file + counter_folder


def balcklist_level(directory, blacklist):
    res = 0.0
    for black in blacklist:
        if black in directory:
            res = res + 1.0
    return res

def has_same_directory_and_name_length(dir1,dir2):
    # Currently disabled feature!
    return False
    #return dir1.split('\\')[:-1] == dir2.split('\\')[:-1] and len(dir1) == len(dir2)

def delete_duplicates_with_rules(blacklist_name, excel_dir):
    with open(blacklist_name) as f: blacklist = f.read()

    blacklist = blacklist.split('\n')
    #print(blacklist)
    # join hash and size, just in case
    file_duplicates = pd.read_excel(excel_dir, sheet_name="DuplicateFiles")
    file_duplicates['Hash'] = file_duplicates[['Size','Hash']].astype(str).apply(' '.join, axis=1)
    
    # Pair of indices, which we use to loop through the list of duplicates
    i = 0 # Pivot index
    j = 1
    
    N = len(file_duplicates)
    deleted_files_so_far = 0
    while (j < N):
        # If duplicate files, process. If not duplicate, move increment pivot index i, and j is the next one
        if file_duplicates.iloc[i]['Hash'] == file_duplicates.iloc[j]['Hash']:
            dir_i = file_duplicates.iloc[i]['Directory']
            dir_j = file_duplicates.iloc[j]['Directory']
            
            # If j ranks higher in the blacklist, and i exists, j is redundant and we delete j
            if blacklist_level(dir_i, blacklist) < blacklist_level(dir_j, blacklist) and exists(dir_i):
                try:
                    os.remove(dir_j)
                    deleted_files_so_far = deleted_files_so_far + 1
                except:
                    'nothing here'
                j = j+1
                
            # If i ranks higher in the blacklist, and j exists, i is redundant and we delete i
            elif blacklist_level(dir_i, blacklist) > blacklist_level(dir_j, blacklist) and exists(dir_j):
                try:
                    os.remove(dir_i)
                    deleted_files_so_far = deleted_files_so_far + 1
                except:
                    'nothing here'
                i = i+1
                j = i+1
            elif has_same_directory_and_name_length(dir_i, dir_j) and exists(dir_i):
                # Currently disabled feature!
                # If two files have same directory and files paths are of same length, delete j. We also make sure i exists
                try:
                    os.remove(dir_j)
                    deleted_files_so_far = deleted_files_so_far + 1
                except:
                    'nothing here'
                j = j+1
            else:
                j=j+1
        else:
            i=i+1
            j=i+1


    file_duplicates['Hash'] = file_duplicates['Hash'].apply(lambda x : x.split(' ')[1])
    print('Deleted ' + str(deleted_files_so_far) + ' files out of duplicate files')
    return deleted
