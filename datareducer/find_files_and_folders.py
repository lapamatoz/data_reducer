import os
import pandas as pd
import datareducer.general

def save_csv(df, name, excel_dir):
    # Saves 'df' as a .csv-file
    df.to_csv(os.path.join(excel_dir, name + '.csv'), index=False, sep=';')

def execute(rootdir, excel_dir):
    bad_folders = pd.DataFrame([],columns=['Reason','Directory','Delete'])
    largest_folders = pd.DataFrame([],columns=['Directory','Size','Delete'])

    subdirectories = [x[0] for x in os.walk(rootdir)]
    
    # LOOP THROUGH ALL FOLDERS

    for subdir in subdirectories:
        directory_path = os.path.join(rootdir, subdir)
        files_in_dir = datareducer.general.list_files(directory_path)
        folders_in_dir = datareducer.general.list_subfolders(directory_path)
        size = len(files_in_dir) + len(folders_in_dir)
        
        if len(files_in_dir) == 0 and len(folders_in_dir) == 0:
            bad_folder = pd.DataFrame([['Empty folder', directory_path]],columns=['Reason','Directory'])
            bad_folders = pd.concat([bad_folders, bad_folder])
        elif datareducer.general.is_temporary(subdir):
            bad_folder = pd.DataFrame([['Temporary folder', directory_path]],columns=['Reason','Directory'])
            bad_folders = pd.concat([bad_folders, bad_folder])
        
        # Update the list of largest folders
        if len(largest_folders) < 200: # <- how many large files to keep in log
            large_folder = pd.DataFrame([[directory_path, size]],columns=['Directory','Size'])
            largest_folders = pd.concat([largest_folders, large_folder])
        elif size > min(largest_folders['Size']):
            largest_folders = largest_folders[largest_folders['Size'] != min(largest_folders['Size'])]
            large_folder = pd.DataFrame([[directory_path, size]],columns=['Directory','Size'])
            largest_folders = pd.concat([largest_folders, large_folder])
            
    largest_folders = largest_folders.sort_values(by=['Size'],ascending=False)
    print('Folders are done!')

    ### LOOP THROUGH ALL FILES

    sizes_list = []
    files_list = []

    bad_files = pd.DataFrame([],columns=['Reason','Directory','Size','Delete'])
    largest_files = pd.DataFrame([],columns=['Directory','Size','Delete'])

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            path = os.path.join(subdir, file)
            try:
                size = os.path.getsize(path)
            except:
                print("Could not find a file. I'll skip it:  " + path)
                continue
            
            files_list.append(path)
            sizes_list.append(size)
            
            if datareducer.general.is_temporary(file):
                bad_file = pd.DataFrame([['Temporary file', path, size]],columns=['Reason','Directory','Size'])
                bad_files = pd.concat([bad_files, bad_file])
                
            if size <= 10:
                bad_file = pd.DataFrame([['Very small file size', path, size]],columns=['Reason','Directory','Size'])
                bad_files = pd.concat([bad_files, bad_file])
            
            # Update the list of largest files
            if len(largest_files) < 200: # <- how many large files to keep in log
                large_file = pd.DataFrame([[path, size]],columns=['Directory','Size'])
                largest_files = pd.concat([largest_files, large_file])
            elif size > min(largest_files['Size']):
                largest_files = largest_files[largest_files['Size'] != min(largest_files['Size'])]
                large_file = pd.DataFrame([[path, size]],columns=['Directory','Size'])
                largest_files = pd.concat([largest_files, large_file])

    print('Files are read, starting the comparison...')

    file_list = pd.DataFrame([files_list, sizes_list])
    file_list = file_list.transpose()
    file_list.columns = ['Directory','Size']

    print('Finding duplicates by size...')
    # first find duplicates sizes, i.e., the size values which appear more than once in the list
    duplicate_sizes = datareducer.general.get_duplicates(file_list['Size'])

    # only keep duplicate sizes
    file_list = file_list[file_list['Size'].isin(duplicate_sizes)]
    
    # next, we find hashes for the largest files, and use blacklist to delete duplicate files as well
    minimum_duplicate_file_list_length = 200
    number_of_files_to_be_hashed = 200
    file_duplicates = pd.DataFrame()
    list_is_short_but_no_more_to_hash = False
    
    # We want at least 200 files in the duplicates list.
    # Some duplicates may vanish from the list due to hash matching, reducing its size.
    # Hashing is time consuming, so we want to minimize the number of files hashed.
    # This loop is here to make sure that there is at least 200 files in the list after hash matching.
    # I.e., we hash more files until there is at least 200 files in the output.

    while len(file_duplicates) < minimum_duplicate_file_list_length and (not list_is_short_but_no_more_to_hash):
        file_duplicates = file_list.sort_values(by=['Size'],ascending=False)
        
        number_of_files_to_be_hashed = min(len(file_list), number_of_files_to_be_hashed)
        
        if number_of_files_to_be_hashed == len(file_list):
            list_is_short_but_no_more_to_hash = True
        else:
            file_duplicates = file_duplicates[file_duplicates['Size'] >= file_duplicates.iloc[number_of_files_to_be_hashed]['Size']]

        print('Evaluating hashes...')
        # find hash for each file
        file_duplicates = file_duplicates.assign(Hash=file_duplicates.apply(datareducer.general.hash_function_1, axis=1))

        # join hash and size, just in case
        file_duplicates['Hash'] = file_duplicates[['Size','Hash']].astype(str).apply(' '.join, axis=1)

        print('Finding duplicate hashes...')
        # find duplicate hashes and remove them from duplicate file list
        duplicate_hashes = datareducer.general.get_duplicates(file_duplicates['Hash'])
        file_duplicates = file_duplicates[file_duplicates['Hash'].isin(duplicate_hashes)]
        
        # double the number of files that are hashed in the next iteration
        number_of_files_to_be_hashed = 2*number_of_files_to_be_hashed

    # Cleaning and sorting
    file_duplicates = file_duplicates.sort_values(by=['Size', 'Hash'],ascending=False)
    file_duplicates['Hash'] = file_duplicates['Hash'].apply(lambda x : x.split(' ')[1])
    file_duplicates['Delete'] = file_duplicates['Size']*float('nan')

    largest_files = largest_files.sort_values(by=['Size'],ascending=False)
    bad_files = bad_files.sort_values(by=['Size'],ascending=False)

    print('Saving csv-files...')
    
    save_csv(file_duplicates, 'DuplicateFiles', excel_dir)
    save_csv(bad_files, 'BadFiles', excel_dir)
    save_csv(bad_folders, 'BadFolders', excel_dir)
    save_csv(largest_files, 'LargestFiles', excel_dir)
    save_csv(largest_folders, 'LargestFolders', excel_dir)

    print('Scan has finished!')
