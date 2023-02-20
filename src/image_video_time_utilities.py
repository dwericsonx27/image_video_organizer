import os
import time

import magic
#pip3 install python-magic

import subprocess
from typing import Dict

import exifread
#pip3 install exifread

import filecmp
from shutil import copyfile
from typing import Tuple

def find_files(source_dir, file_ext):
    for dirpath, dirnames, filenames in os.walk(source_dir):
        for f_name in filenames:
            if f_name.endswith(file_ext):
                yield os.path.join(dirpath, f_name)
                
def process_args(arg_list) -> Tuple[bool, str, str]:
    if len(arg_list) == 3:
        return True, arg_list[1], arg_list[2]
    else:
        return False, "", ""

def process_folder(src_folder, dst_folder) -> None:
    f_types = magic.Magic(mime=True)
    occurences: Dict[str, int] = {}

    try:
        for fullpath_filename in find_files(src_folder, ""):
            file_type = None
            try:
                file_type = f_types.from_file(fullpath_filename)
                print(f"filename : {fullpath_filename}, {file_type}")
                if file_type == "image/jpeg": 
                    process_image(fullpath_filename, dst_folder, "jpg")

                elif file_type == "video/mp4":
                    process_mp4(fullpath_filename, dst_folder)

                elif file_type == "video/x-msvideo":
                    process_video(fullpath_filename, dst_folder)

                elif file_type == "video/quicktime":
                    process_video(fullpath_filename, dst_folder)

                elif file_type == "image/tiff":
                    process_image(fullpath_filename, dst_folder, "NEF")

            except Exception as e:
                print(f"file type exception : {e}")

    except FileNotFoundError:
        print(f"ERROR: source directory ({source_dir}) does not exist!")

    except Exception as e:
        print(f"ERROR: {e}")


def identical_file_already_exists(out_dir: str, file_name_no_extension: str, src_full_filename: str) -> bool:
    if len(out_dir) == 0:
        return False
    if len(file_name_no_extension) == 0:
        return False
    if len(src_full_filename) == 0:
        return False
    
    if os.path.exists(out_dir):
        file_list = os.listdir(out_dir)
        for f in file_list:
            if f.find(file_name_no_extension) >= 0:  #note that extension name can not be guarenteed
                found_name = os.path.join(out_dir, f)
                if filecmp.cmp(found_name, src_full_filename):
                    return True
    return False

def process_image(fullpath_filename: str, dest_dir: str, extention: str) -> None:
    try:
        year, hr_min_sec, filename, yyyymmdd_hhmmss, mon, day, hr, min, sec, model = jpeg_name(fullpath_filename)
        out_dir = os.path.join(os.path.join(dest_dir, year), hr_min_sec)
        out_file = os.path.join(out_dir, filename)
        if os.path.isfile(out_file):
            if filecmp.cmp(out_file, fullpath_filename):
                print(f'DELETE {fullpath_filename}.')
                time.sleep(0.2)
                os.remove(fullpath_filename)
            else:
                print(f'COPY {fullpath_filename} ADD UNIQUE DESIGNATOR.')
                i = 1
                out_file = os.path.join(out_dir, f'{year}{mon}{day}_{hr}{min}{sec}_{model}_{i}.{extention}' )
                while os.path.isfile(out_file):
                    i = i + 1
                    out_file = os.path.join(out_dir, f'{year}{mon}{day}_{hr}{min}{sec}_{model}_{i}.{extention}' )
                # Copy file over.
                os.makedirs(out_dir, exist_ok=True)
                copyfile(fullpath_filename, out_file)
                os.remove(fullpath_filename)
                print(f'Copied {fullpath_filename} to {out_file}')
        else:
            # Open the directory and look for a file of a similar name.
            if identical_file_already_exists(out_dir, yyyymmdd_hhmmss, fullpath_filename):
                print(f'DELETE {fullpath_filename}.')
                time.sleep(0.2)
                os.remove(fullpath_filename)
                # so we should be able to delete the source....
            else:
                # Copy file over.
                os.makedirs(out_dir, exist_ok=True)
                copyfile(fullpath_filename, out_file)
                os.remove(fullpath_filename)
                print(f'Copied {fullpath_filename} to {out_file}')
    except Exception as e:
        print(f'EXIF data not found, using media info instead.')
        try:
            process_video(fullpath_filename, dest_dir)
            print(f'EXIF data not found, using media info instead.')
        except Exception as e2:
            print(f'Exception: {e2}')

def jpeg_name(image_file_name: str) -> Tuple[str, str, str, str, str, str, str, str, str, str] :

    with open(image_file_name, 'rb') as image_file:
        tags = exifread.process_file(image_file)

        try:
            origination = str(tags["EXIF DateTimeOriginal"])

            model = str(tags["Image Model"]).replace(" ", "-").upper()
            #  COOLPIX P600
            # filename: 20190112_114819_SM-S906L
            # directory: 2019_01_12

            yearmonday = origination[0:10].replace(":", "")
            year = yearmonday[0:4]
            mon = yearmonday[4:6]
            day = yearmonday[6:8]
           
            year_mon_day = f'{year}_{mon}_{day}'
            hrminsec = origination[11:19].replace(":", "")
            hr = hrminsec[0:2]
            min = hrminsec[2:4]
            sec = hrminsec[4:6]

            file_time= f'{yearmonday}_{hrminsec}'
            file_name = f'{file_time}_{model}.jpg'

            return year, year_mon_day, file_name, file_time, mon, day, hr, min, sec, model
        except Exception as e:
            print(f'EXIF DateTimeOriginal not found!')
            print(f'number of tags = {len(tags)}')
            print(f'tags: {type(tags)}')
            for t in tags:
                print(f'tag: {t}')
            print("========================================")
            raise e


def process_mp4(file_name: str, dest_dir: str) -> None:
    pass

def process_video(file_name: str, dest_dir: str) -> None:
    # Set the command
    command = f'mediainfo -f {file_name}'

    # Setup the module object
    proc = subprocess.Popen(command,
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    # Communicate the command
    stdout_value,stderr_value = proc.communicate()

    # Once you have a valid response, split the return output
    if stdout_value:
        stdout_values = str(stdout_value).split('\\n')
        found = False
        for tag in ['Mastered date', 'File last modification date (local)']:
            for s in stdout_values:
                # print(f's : {s}')
                if s.find(tag) >= 0:
                    found = True
                    colon_pos = s.find(':')
                    date = s[colon_pos+2:]
                    mon = date[4:7]
                    day = ''
                    year = ''
                    min = ''
                    hr = ''
                    sec = ''

                    mon_2_num = { 'JAN': '01',
                                  'FEB': '02',
                                  'MAR': '03',
                                  'APR': '04',
                                  'MAY': '05',
                                  'JUN': '06',
                                  'JUL': '07',
                                  'AUG': '08',
                                  'SEP': '09',
                                  'OCT': '10',
                                  'NOV': '11',
                                  'DEC': '12' }

                    not_found = '99'

                    num_mon = mon_2_num.get(mon, not_found)

                    if num_mon != not_found:
                        year = date[20:]
                        day = date[8:10]
                        mon = num_mon
                        hr = date[11:13]
                        min = date[14:16]
                        sec = date[17:19]
                    else:
                        year = date[0:4]
                        mon = date[5:7]
                        day = date[8:10]
                        hr = date[11:13]
                        min = date[14:16]
                        sec = date[17:19]

                    if not 1970 <= int(year) <= 2050:
                        print('bad year')
                        return

                    if not 1 <= int(mon) <= 12:
                        print('bad mon')
                        return

                    if not 1 <= int(day) <= 31:
                        print('bad day')
                        return

                    if not 0 <= int(hr) <= 24:
                        print('bad hr')
                        return

                    if not 0 <= int(min) <= 60:
                        print('bad min')
                        return

                    if not 0 <= int(sec) <= 60:
                        print('bad sec')
                        return

                    out_dir = os.path.join(os.path.join(dest_dir, year), f'{year}_{mon}_{day}')
                    extention = file_name[-3:]
                    out_file = os.path.join(out_dir, f'{year}{mon}{day}_{hr}{min}{sec}.{extention}' )
                    print(f'out_file = {out_file}')
                    if os.path.isfile(out_file):
                        if filecmp.cmp(out_file, file_name):
                            print(f'DELETE {file_name}.')
                            time.sleep(0.2)
                            os.remove(file_name)
                        else:
                            print(f'COPY {file_name} ADD UNIQUE DESIGNATOR.')
                            i = 1
                            out_file = os.path.join(out_dir, f'{year}{mon}{day}_{hr}{min}{sec}_{i}.{extention}' )
                            while os.path.isfile(out_file):
                                i = i + 1
                                out_file = os.path.join(out_dir, f'{year}{mon}{day}_{hr}{min}{sec}_{i}.{extention}' )
                            # Copy file over.
                            os.makedirs(out_dir, exist_ok=True)
                            copyfile(file_name, out_file)
                            os.remove(file_name)
                            print(f'Copied {file_name} to {out_file}')
                    else:
                        # Open the directory and look for a file of a similar name.
                        file_time= f'{year}{mon}{day}_{hr}{min}{sec}'
                        if identical_file_already_exists(out_dir, file_time, file_name):
                            print(f'DELETE {file_name}.')
                            time.sleep(0.2)
                            os.remove(file_name)
                            # so we should be able to delete the source....
                        else:
                            # Copy file over.
                            os.makedirs(out_dir, exist_ok=True)
                            copyfile(file_name, out_file)
                            os.remove(file_name)
                            print(f'Copied {file_name} to {out_file}')
                if found:
                    break;
            if found:
                break;

        if found == False:
            print(f'Date tag not found in file: {file_name}')
            for s in stdout_values:
                print(f'tag: {s}')
