import os
from tqdm import tqdm

def rename_frames(basefilename="image"):
    ROOT = "highres"
    subdirs = os.listdir(ROOT)

    # Iterate through all subdirectories
    for subdir in subdirs:
        subdir_full_path = os.path.join(ROOT, subdir)
        # Make sure the current file is a directory
        if not os.path.isdir(subdir_full_path):
            continue
        
        # Get all files in the subdir
        filenames = os.listdir(subdir_full_path)
        
        # set up counter for file names
        counter = 1
        for filename in tqdm(filenames, desc=f"Renaming files in {subdir_full_path}"):
            ext = filename.split('.')[-1]
            file_full_path = os.path.join(subdir_full_path, filename)
            new_file_path = os.path.join(subdir_full_path, f"image{counter:04d}.{ext}")
            counter += 1
            os.rename(file_full_path, new_file_path)
    
    return counter

if __name__ == "__main__":
    rename_frames()
    input("Press any key to continue\n")
