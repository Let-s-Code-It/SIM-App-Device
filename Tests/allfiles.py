import glob
dir_path = r'../App/**'
for file in glob.glob(dir_path, recursive=True):
    print(file)