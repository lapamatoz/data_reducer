import os
import pandas as pd
import datareducer.general as general

### FOLDERS

def save_csv_nonempty(df, name, excel_dir):
    #if len(df) > 0:
    df.to_csv(os.path.join(excel_dir, name + '.csv'), index=False, sep=';')

def execute(rootdir, excel_dir, excel_file_name):
    bad_folders = pd.DataFrame([],columns=['Reason','Directory','Delete'])
    largest_folders = pd.DataFrame([],columns=['Directory','Size','Delete'])

    subdirectories = [x[0] for x in os.walk(rootdir)]

    for subdir in subdirectories:
        directory_path = os.path.join(rootdir, subdir)
        files_in_dir = general.list_files(directory_path)
        folders_in_dir = general.list_subfolders(directory_path)
        size = len(files_in_dir) + len(folders_in_dir)
        if len(files_in_dir) == 0 and len(folders_in_dir) == 0:
            bad_folder = pd.DataFrame([['Empty folder', directory_path]],columns=['Reason','Directory'])
            bad_folders = pd.concat([bad_folders, bad_folder])
        #elif len(files_in_dir) <= 1 and len(folders_in_dir) <= 1:
        #    bad_folder = pd.DataFrame([['Almost empty folder', directory_path]],columns=['Reason','Directory'])
        #    bad_folders = pd.concat([bad_folders, bad_folder])
        elif general.is_temporary(subdir):
            bad_folder = pd.DataFrame([['Temporary folder', directory_path]],columns=['Reason','Directory'])
            bad_folders = pd.concat([bad_folders, bad_folder])
            
        if len(largest_folders) < 200: # <- how many large files to keep in log
            large_folder = pd.DataFrame([[directory_path, size]],columns=['Directory','Size'])
            largest_folders = pd.concat([largest_folders, large_folder])
        elif size > min(largest_folders['Size']):
            largest_folders = largest_folders[largest_folders['Size'] != min(largest_folders['Size'])]
            large_folder = pd.DataFrame([[directory_path, size]],columns=['Directory','Size'])
            largest_folders = pd.concat([largest_folders, large_folder])
            
    #print(bad_folders)
    largest_folders = largest_folders.sort_values(by=['Size'],ascending=False)
    print('Folders are done!')

    ### FILES

    sizes_list = []
    files_list = []

    bad_files = pd.DataFrame([],columns=['Reason','Directory','Size','Delete'])
    largest_files = pd.DataFrame([],columns=['Directory','Size','Delete'])

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            
            path = os.path.join(subdir, file)
            size = os.path.getsize(path)
            
            files_list.append(path)
            sizes_list.append(size)
            
            if general.is_temporary(file):
                bad_file = pd.DataFrame([['Temporary file', path, size]],columns=['Reason','Directory','Size'])
                bad_files = pd.concat([bad_files, bad_file])
            
            if path[-4:] == '.exe':
                bad_file = pd.DataFrame([['Executable file', path, size]],columns=['Reason','Directory','Size'])
                bad_files = pd.concat([bad_files, bad_file])
                
            if path[-4:] == '.msi':
                bad_file = pd.DataFrame([['Executable file', path, size]],columns=['Reason','Directory','Size'])
                bad_files = pd.concat([bad_files, bad_file])
                
            if size <= 10:
                bad_file = pd.DataFrame([['Very small file size', path, size]],columns=['Reason','Directory','Size'])
                bad_files = pd.concat([bad_files, bad_file])
            
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

    # FIND DUPLICATE FILE SIZES

    print('Finding duplicates by size...')
    # first find duplicates by size
    duplicate_sizes = general.get_duplicates(file_list['Size'])

    # only keep duplicate sizes
    file_list = file_list[file_list['Size'].isin(duplicate_sizes)]

    number_of_files_to_be_hashed = 200
    file_duplicates = pd.DataFrame()
    number_of_files_to_be_hashed_is_small = True

    while len(file_duplicates) < 200 and number_of_files_to_be_hashed_is_small:
        file_duplicates = file_list.sort_values(by=['Size'],ascending=False)
        
        number_of_files_to_be_hashed = min(len(file_list), number_of_files_to_be_hashed)
        
        if number_of_files_to_be_hashed == len(file_list):
            number_of_files_to_be_hashed_is_small = False
        else:
            file_duplicates = file_duplicates[file_duplicates['Size'] >= file_duplicates.iloc[number_of_files_to_be_hashed]['Size']]

        print('Evaluating hashes...')
        # find hash for each file
        file_duplicates = file_duplicates.assign(Hash=file_duplicates.apply(general.hash_function_1, axis=1))

        # join hash and size, just in case
        file_duplicates['Hash'] = file_duplicates[['Size','Hash']].astype(str).apply(' '.join, axis=1)

        print('Finding duplicate hashes...')
        # find duplicate hashes and remove them from duplicate file list
        duplicate_hashes = general.get_duplicates(file_duplicates['Hash'])
        file_duplicates = file_duplicates[file_duplicates['Hash'].isin(duplicate_hashes)]
        number_of_files_to_be_hashed = 2*number_of_files_to_be_hashed

    # Cleaning
    file_duplicates = file_duplicates.sort_values(by=['Size', 'Hash'],ascending=False)
    file_duplicates['Hash'] = file_duplicates['Hash'].apply(lambda x : x.split(' ')[1])
    file_duplicates['Delete'] = file_duplicates['Size']*float('nan')

    largest_files = largest_files.sort_values(by=['Size'],ascending=False)
    bad_files = bad_files.sort_values(by=['Size'],ascending=False)

    print('Saving Excel-file...')

    os.chdir(excel_dir)

    '''
    def highlight_cells(x):
        # provide your criteria for highlighting the cells here
        return ['background-color: yellow']

    def bg_header(x):
        return "background-color: grey"
        
    bad_files2 = bad_files.style.applymap_index(bg_header, axis=1)
    '''
    # = bad_files.style.apply(highlight_cells)
    #try:
    '''
    with pd.ExcelWriter(excel_file_name) as writer:
        file_duplicates.to_excel(writer, sheet_name='DuplicateFiles',index=False)
        bad_files.to_excel(      writer, sheet_name='BadFiles',      index=False)
        bad_folders.to_excel(    writer, sheet_name='BadFolders',    index=False)
        largest_files.to_excel(  writer, sheet_name='LargestFiles',  index=False)
        largest_folders.to_excel(writer, sheet_name='LargestFolders',index=False)
    '''
    save_csv_nonempty(file_duplicates, 'DuplicateFiles', excel_dir)
    save_csv_nonempty(bad_files, 'BadFiles', excel_dir)
    save_csv_nonempty(bad_folders, 'BadFolders', excel_dir)
    save_csv_nonempty(largest_files, 'LargestFiles', excel_dir)
    save_csv_nonempty(largest_folders, 'LargestFolders', excel_dir)

    print('All done!')