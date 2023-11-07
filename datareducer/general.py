import os, re, hashlib
import pandas as pd
from collections import Counter
from functools import cache

def is_temporary(x):
    strs = ['tmp', 'temp', 'autosave', 'backup', 'checkpoint', 'cache', 'preview']
    for s in strs:
        if re.search(s, x, re.IGNORECASE):
            return True
    return False

def list_files(P):
    return [f for f in os.listdir(P) if os.path.isfile(os.path.join(P, f))]

def list_subfolders(P):
    return [f for f in os.listdir(P) if not os.path.isfile(os.path.join(P, f))]

@cache # Hashes are evaluated many times, primarly due to bad coding :D This was an easy way to make it a lot faster
def hash_function_large_file(file_dir):
    # Credit: https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    # BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    BUF_SIZE = 1000000 # time-optimized for large files, but do re-optimize if necessary
    md5 = hashlib.md5()
    with open(file_dir, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def get_duplicates(array): # a linear time function!
    c = Counter(array)
    return [k for k in c if c[k] > 1] 

def hash_function_1(array): # Used with Pandas apply-function
    return hash_function_large_file(array.iloc[0]) # First column must be 'Directory'!