# Import hashlib library (md5 method is part of it)
import hashlib

# File to check
file_name = '../App/SQL.py'

# Correct original md5 goes here
original_md5 = '5d41402abc4b2a76b9719d911017c592'  

# Open,close, read file and calculate MD5 on its contents 
with open(file_name, 'rb') as file_to_check:
    # read contents of the file
    data = file_to_check.read()    
    # pipe contents of the file through
    md5_returned = hashlib.md5(data).hexdigest()

print(md5_returned)