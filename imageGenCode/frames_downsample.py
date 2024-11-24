import os
from PIL import Image, ImageFilter
from tqdm import tqdm
import random
import numpy as np

def get_image_paths(path: str) -> list[str]:
    """Recursively gets paths to all images in the directory
    Args:
        path (str): The path to the current directory

    Returns:
        list[str]: list of paths to jpg files
    """
    output = []
    subdirs = set()
    # Look at all items in the current folder
    items = os.listdir(path)
    for item in items:
        path_to_dir = os.path.join(path, item)
        # Check if the current item is a folder
        if os.path.isdir(path_to_dir):
            subdirs.add(item)
            video_paths = get_image_paths(path_to_dir)
            output.extend(video_paths)
        # If the current item is a video, just add it to the output
        elif path_to_dir.split('.')[-1] in ['jpg']:
            output.append(path_to_dir)
    
    # Create missing subdirs
    for item in subdirs:
        lowres_subdir_path = os.path.join("lowres", item)
        if not os.path.exists(lowres_subdir_path):
            os.mkdir(lowres_subdir_path)
    return output

def process_image(original: Image, effect_rate: int = 33) -> Image:
    """Applies effects and resizes image

    Args:
        original (Image): The Image object of the original image
        effect_rate (int, optional): The chance of an effect being applied (33). Defaults to 33.

    Returns:
        Image: The processed image file
    """    
    # Calculate new size of height
    width, height = original.size
    aspect_ratio = width/height
    new_height = 270
    new_width = int(new_height * aspect_ratio)
    
    # Resize image
    random_int = random.randint(0, 3)
    if random_int == 0:
        resample = Image.BILINEAR
    elif random_int == 1:
        resample = Image.BICUBIC
    else:
        resample = Image.LANCZOS
    downsampled = original.resize((new_width, new_height), resample)
    
    # Add blur / noise
    add_effect = random.randint(0, 100) < effect_rate
    if add_effect:
        # do_blur = random.randint(0, 3) == 0
        # if do_blur:
        #     blur_effect = random.randint(0, 2)
        #     if blur_effect == 0:
        #         blur = ImageFilter.GaussianBlur(random.uniform(0, 1))
        #     elif blur_effect == 1:
        #         blur = ImageFilter.BLUR
        #     else:
        #         blur = ImageFilter.BoxBlur(random.uniform(0, 1))
        #     downsampled = downsampled.filter(blur)
        # else:
        mean = 0
        stddev = random.uniform(5, 20)
        downsampled_array = np.array(downsampled)
        noise = np.random.normal(mean, stddev, downsampled_array.shape).astype(np.int16)
        downsampled = np.clip(downsampled_array + noise, 0, 255).astype(np.uint8)
        downsampled = Image.fromarray(downsampled)

    return downsampled
    

if __name__ == "__main__":
    lowres_folder = "lowres"
    highres_folder = "highres"
    random.seed(2024)
    
    # create lowres folder if it does not exist
    if not os.path.exists(lowres_folder):
        os.makedirs(lowres_folder)
               
    # Get each path to the highres file
    highres_filepaths = get_image_paths(highres_folder)
    for highres_filepath in tqdm(highres_filepaths, desc="Processing Images"):
        # Create path to lowres version of this file
        lowres_filepath = "\\".join(highres_filepath.split('\\')[1:])
        lowres_filepath = os.path.join(lowres_folder, lowres_filepath)
        
        # load higres image
        image = Image.open(highres_filepath)
        downsampled = process_image(image, 33)
        
        # Save image
        downsampled.save(lowres_filepath)
    
    input("Press any key to continue\n")               
