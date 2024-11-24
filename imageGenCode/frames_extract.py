import os
import subprocess
import xml.etree.ElementTree as ET
from tqdm import tqdm
import time

from frames_rename import rename_frames

# We don't want to include Opening and Endings because they will create a lot of copies
chapters_to_exclude = ['OP', 'ED', 'Opening', 'Ending', 'Preview', 'Credits Start', 'Recap Start', 'Recap', 'Eyecatch']

def get_video_paths(path: str) -> list[str]:
    """
    Recursively pulls video paths from directory
    Args:
        path (str): path to specific directory

    Returns:
        list[str]: list of paths to mkv files
    """
    output = []
    # Look at all items in the current folder
    items = os.listdir(path)
    for item in items:
        path_to_dir = os.path.join(path, item)
        # Check if the current item is a folder
        if os.path.isdir(path_to_dir):
            video_paths = get_video_paths(path_to_dir)
            output.extend(video_paths)
        # If the current item is a video, just add it to the output
        elif path_to_dir.split('.')[-1] in ['mkv']:
            output.append(path_to_dir)
    
    return output
    
def get_mkv_include_times(path: str) -> list[tuple]:
    """
    Gets times of chapters to exclude
    Args:
        path (str): path to specific video 

    Returns:
        list[tuple]: a list of start and end times for chapters
    """
    if not path[-3:] == "mkv":
        return
    
    command = ['mkvextract', "chapters", path]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        print(f"Error extracting chapters: {result.stderr}")
        return None
    
    # Data is outputted as XML
    result = result.stdout
    if result.startswith("ï»¿"):
        result = result[3:]
    
    try:
        xml_root = ET.fromstring(result)
        pass
    except Exception as e:
        print(result)
        return None
        
    times = []
    chapter_atoms = xml_root.findall(".//ChapterAtom")
    # Go through all chapters and take not of chapters we want to exclude 
    for i, chapter_atom in enumerate(chapter_atoms):
        chapter_name = chapter_atom.find('.//ChapterString').text
        # If this chapter is not in the exclusion list, use its times
        if chapter_name not in chapters_to_exclude:
            time_start = chapter_atom.find('ChapterTimeStart').text
            if i + 1 >= len(chapter_atoms):
                time_end = None
            else:
                time_end = chapter_atoms[i+1].find('ChapterTimeStart').text
            # print(chapter_name, time_start, time_end)
            times.append((time_start, time_end))
        
    return times

def generate_frames(folder_name: str, base_file_name: str, mkv_path: str, times: tuple[str]=None):
    """generate jpg images every 15 seconds of a vide

    Args:
        folder_name (str): folder to save to
        base_file_name (str): used to generate names for image files
        mkv_path (str): mkv file to use
        times (tuple[str], optional): the duration of . Defaults to None.
    """
    folder_to_save_to = os.path.join("highres", folder_name)
    # Get a frame every fifteen seconds
    fps = 'fps=1/15'
    # Make sure to create the folder where each frame will be saved
    if not os.path.exists(folder_to_save_to):
        os.makedirs(folder_to_save_to)
        
    # This base command will be reused for both time and no time
    base_ffmpeg_command = ["ffmpeg", "-i", mkv_path, "-vf", fps, "-q:v", "1", "-vsync", "vfr"]
    
    # If no timings were provided, then go through whole file
    if times is None:
        true_file_name = f"{base_file_name[:-4]}"
        final_path = os.path.join(folder_to_save_to, true_file_name)
        output_file = f"{final_path}_%04d.jpg"
        ffmpeg_command = base_ffmpeg_command + [output_file]
        # This try and catch just makes sure we don't quit the program if conversion fails
        try:
            out = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception as e:
            pass
    # If there are timings, go through each set of times (start and end time)
    else:
        for idx, time in enumerate(times):
            start_time, end_time = time
            # We add index to the file name because we will be running the frame generate multiple times
            true_file_name = f"{base_file_name[:-4]}_{idx}"
            final_path = os.path.join(folder_to_save_to, true_file_name)
            output_file = f"{final_path}_%04d.jpg"
            
            # Add start time and end time to the command
            ffmpeg_command = base_ffmpeg_command + ['-ss', start_time]
            if end_time is not None:
                ffmpeg_command = ffmpeg_command + ['-to', end_time]
            # Add output file name
            ffmpeg_command = ffmpeg_command + [output_file]
            
            try:
                subprocess.run(ffmpeg_command, check=True)
                #subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except Exception as e:
                pass

if __name__ == "__main__":
    # Make highres folder if it does not exist
    if not os.path.exists("highres"):
        os.makedirs("highres")
    
    dirs = os.listdir()
    # First we enter the main directory
    print('Beginning Frame Extraction.')
    startTime = time.time()
    for dir in dirs:
        # In the main directory we only want to look for folders leading to specific animes
        if not os.path.isdir(dir):
            continue
        elif dir == "highres":
            continue
        elif dir == "lowres":
            continue
        
        # We get all video files in each subfolder using a recursive function
        video_paths = get_video_paths(dir)
            
        # These lines here determine what the name of the final file will be
        subfolder_name = dir
        # Go through each video to generate pngs
        for video_path in tqdm(video_paths, desc=f"Extracting from {dir} folder"):
            # This gets the timings for openings and endings for exclusion
            times = get_mkv_include_times(video_path)
            
            filename = video_path.replace(' ', '').split('\\')[-1]
            generate_frames(subfolder_name, filename, video_path, times)
    endTime = time.time()
    elapsedTime = endTime - startTime
    print(f"Extracting Done! It took {elapsedTime:0.2f}s")
    
    print("Renaming files")
    rename_frames()
    
    input("Press any key to continue\n")        