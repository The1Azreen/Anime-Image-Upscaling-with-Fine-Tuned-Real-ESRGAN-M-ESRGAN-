import pandas as pd
import random
import os

if __name__ == "__main__":
    # Technically you only need highres to do everything in this file
    # I'm only adding this line to remind myself that I should generate downsampled versions
    if not (os.path.exists("highres") and os.path.exists('lowres')):
        print("Either highres or lowres folder does not exist. Please generate them.")
        print("highres can be generated using frames-extract.py.")
        print("lowres can be generated using frames-downsample.py.")
        
    # Set seed
    random.seed(2024)
    # Set split of data
    TRAIN, TEST, VAL = 0.7, 0.15, 0.15
    
    # storing all this data on this df
    # subdir is the subdir in highres or highres
    # type is TRAIN, TEST, VAL
    output_data = []
    
    # Go through every subfolder in the highres folder
    ROOT = "highres"
    subdirs = os.listdir(ROOT)
    for subdir in subdirs:
        subdir_path = os.path.join(ROOT, subdir)
        # If the current item is not a directory, move on to the next item
        # Doing this cause, we'll be looking INSIDE the folders, so I wanna avoid any potential crashes
        if not os.path.isdir(subdir_path):
            continue
        
        # Now we go into each subfolder and get the path of each image
        subdir_items = os.listdir(subdir_path)
        for subdir_item in subdir_items:
            highres_filepath = os.path.join(subdir_path, subdir_item)
            lowres_filepath = os.path.join("lowres", subdir, subdir_item)
            item_type = random.choices(['TRAIN', 'TEST', 'VAL'], weights=[TRAIN, TEST, VAL], k=1)[0]
            data = {'highres': highres_filepath,
                    "lowres": lowres_filepath,
                    "type": item_type }
            output_data.append(data)
            
    # Save to csv
    output_df = pd.DataFrame(output_data)
    output_df.to_csv("paths.csv", index=False, encoding='utf-8')

    # Print the distribution of each type
    distribution = output_df['type'].value_counts(normalize=True) * 100
    print("Expected distribution:")
    print(f"TRAIN: {TRAIN}, TEST: {TEST}, VAL: {VAL}\n")
    
    print("Actual Distribution:")
    print(distribution)
    
    input("Press any key to continue\n")