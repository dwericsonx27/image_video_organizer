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

# TODO: abstract types here
from msg_logger import MsgLogger, LogEntryType

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
        
def jpeg_info(image_file_name : str, logger: MsgLogger) -> Dict:
    info = dict()

    with open(image_file_name, 'rb') as image_file:
        tags = exifread.process_file(image_file)

        try:
            origination = str(tags["EXIF DateTimeOriginal"])

            info['model'] = str(tags["Image Model"]).replace(" ", "-").upper()
            #  COOLPIX P600
            # filename: 20190112_114819_SM-S906L
            # directory: 2019_01_12

            yearmonday = origination[0:10].replace(":", "")
            info['year'] = yearmonday[0:4]
            info['mon'] = yearmonday[4:6]
            info['day'] = yearmonday[6:8]
            info['year_mon_day'] = f"{info['year']}_{info['mon']}_{info['day']}"

            hrminsec = origination[11:19].replace(":", "")
            info['hr'] = hrminsec[0:2]
            info['min'] = hrminsec[2:4]
            info['sec'] = hrminsec[4:6]
            info['hr_min_sec'] = f"{info['hr']}_{info['min']}_{info['sec']}"

            info['yyyymmdd_hhmmss'] = f"{info['year']}{info['mon']}{info['day']}_{info['hr']}{info['min']}{info['sec']}"

            info['file_time'] = f'{yearmonday}_{hrminsec}'
            info['file_name'] = f"{info['file_time']}_{info['model']}.jpg"

            return info
        except Exception as e:
            logger.add_log(f"Fail to acquire all needed tags from {image_file_name}.", LogEntryType.Error)
            print(f'EXIF DateTimeOriginal not found!')
            print(f'number of tags = {len(tags)}')
            print(f'tags: {type(tags)}')
            for t in tags:
                print(f'tag: {t}')
            print("========================================")
            raise e
        

def ok_tags(info : Dict, logger: MsgLogger) -> bool:
    return_value: bool = True

    if not info.get('model'):
        logger.add_log("Missing Tag: model", LogEntryType.Error)
        return_value = False    
    elif len(info['model']) < 1:
        logger.add_log("Tag: model - empty", LogEntryType.Error)
        return_value = False
    
    if not info.get('year'):
        logger.add_log("Missing Tag: year", LogEntryType.Error)
        return_value = False
    elif len(info['year']) != 4:
        logger.add_log("Tag: year - invalid size", LogEntryType.Error)
        return_value = False
    elif int(info['year']) >= 3000:
        logger.add_log(f"Tag: year - to large ({info['year']})", LogEntryType.Error)
        return_value = False
    elif int(info['year']) < 0:
        logger.add_log(f"Tag: year - to small ({info['year']})", LogEntryType.Error)
        return_value = False
    
    if not info.get('mon'):
        logger.add_log("Missing Tag: mon", LogEntryType.Error)
        return_value = False
    elif len(info['mon']) != 2:
        logger.add_log(f"Tag: mon - character count is not 2 ({info['mon']})", LogEntryType.Error)
        return_value = False
    elif int(info['mon']) >= 13:
        logger.add_log(f"Tag: mon - value too large ({info['mon']})", LogEntryType.Error)
        return_value = False
    elif int(info['mon']) < 1:
        logger.add_log(f"Tag: mon - value too small ({info['mon']})", LogEntryType.Error)
        return_value = False
    
    if not info.get('day'):
        logger.add_log("Missing Tag: day", LogEntryType.Error)
        return_value = False
    elif len(info['day']) != 2:
        logger.add_log(f"Tag: day - character count is not 2 ({info['day']})", LogEntryType.Error)
        return_value = False
    elif int(info['day']) >= 32:
        logger.add_log(f"Tag: day - value too large ({info['day']})", LogEntryType.Error)
        return_value = False
    elif int(info['day']) <= 0:
        logger.add_log(f"Tag: day - value too small ({info['day']})", LogEntryType.Error)
        return_value = False
    
    if not info.get('hr'):
        logger.add_log("Missing Tag: hr", LogEntryType.Error)
        return_value = False
    elif len(info['hr']) != 2:
        logger.add_log(f"Tag: hr - character count is not 2 ({info['hr']})", LogEntryType.Error)
        return_value = False
    elif int(info['hr']) >= 24:
        logger.add_log(f"Tag: hr - value too large ({info['hr']})", LogEntryType.Error)
        return_value = False
    elif int(info['hr']) < 0:
        logger.add_log(f"Tag: hr - value too small ({info['hr']})", LogEntryType.Error)
        return_value = False
    
    if not info.get('min'):
        logger.add_log("Missing Tag: min", LogEntryType.Error)
        return_value = False
    elif len(info['min']) != 2:
        logger.add_log(f"Tag: min - character count is not 2 ({info['min']})", LogEntryType.Error)
        return_value = False
    elif int(info['min']) >= 60:
        logger.add_log(f"Tag: min - value too large ({info['min']})", LogEntryType.Error)
        return_value = False
    elif int(info['min']) < 0:
        logger.add_log(f"Tag: min - value too small ({info['min']})", LogEntryType.Error)
        return_value = False
    
    if not info.get('sec'):
        logger.add_log("Missing Tag: sec", LogEntryType.Error)
        return_value = False
    elif len(info['sec']) != 2:
        logger.add_log(f"Tag: sec - character count is not 2 ({info['sec']})", LogEntryType.Error)
        return_value = False
    elif int(info['sec']) >= 60:
        logger.add_log(f"Tag: sec - value too large ({info['sec']})", LogEntryType.Error)
        return_value = False
    elif int(info['sec']) < 0:
        logger.add_log(f"Tag: sec - value too small ({info['sec']})", LogEntryType.Error)
        return_value = False
    
    if not info.get('hr_min_sec'):
        logger.add_log("Missing Composite Tag: hr_min_sec", LogEntryType.Error)
        return_value = False
    elif len(info['hr_min_sec']) != 8:
        logger.add_log(f"Composite Tag: hr_min_sec - character count is not 8 ({info['hr_min_sec']})", LogEntryType.Error)
        return_value = False
    
    if not info.get('year_mon_day'):
        logger.add_log("Missing Composite Tag: year_mon_day", LogEntryType.Error)
        return_value = False
    elif len(info['year_mon_day']) != 10:
        logger.add_log(f"Composite Tag: year_mon_day - character count is not 10 ({info['year_mon_day']})", LogEntryType.Error)
        return_value = False
    
    if not info.get('file_time'):
        logger.add_log("Missing Composite Tag: file_time", LogEntryType.Error)
        return_value = False
    elif len(info['file_time']) != 15:
        logger.add_log(f"Composite Tag: file_time - character count is not 15 ({info['file_time']})", LogEntryType.Error)
        return_value = False
    
    if not info.get('file_name'):
        logger.add_log("Missing Composite Tag: file_name", LogEntryType.Error)
        return_value = False
    elif len(info['file_name']) < 15:
        logger.add_log(f"Composite Tag: file_name - character count is not at least 15 ({info['file_name']})", LogEntryType.Error)
        return_value = False
    
    return return_value

def copy_file(src_fullpath_filename: str, dest_folder: str, dest_fullpath_filename: str, logger: MsgLogger) -> bool:
    try:
        os.makedirs(dest_folder, exist_ok=True)
        copyfile(src_fullpath_filename, dest_fullpath_filename)
    except Exception as e:
        logger.add_log(f"Copy file error: {src_fullpath_filename} to {dest_folder} {dest_fullpath_filename}", LogEntryType.Error)
        print(f'Exception: {e}')


def process_file(src_fullpath_filename: str, dest_folder: str, file_extention: str, info : Dict, logger: MsgLogger) -> bool:
    try:
        dest_folder = os.path.join(os.path.join(dest_folder, info['year']), info['hr_min_sec'])
        dest_fullpath_filename = os.path.join(dest_folder, info['file_name'])
        if os.path.isfile(dest_fullpath_filename):
            # Destination file already exists
            if filecmp.cmp(dest_fullpath_filename, src_fullpath_filename):
                # Existing destination file and src file are the same, so delete the src file.
                print(f'DELETE {src_fullpath_filename}.')
                time.sleep(0.2)
                os.remove(src_fullpath_filename)
            else:
                # Existing desination file have different contents.  Create unique index, so file
                # can be copied over.
                print(f'COPY {src_fullpath_filename} ADD UNIQUE DESIGNATOR.')
                i = 1
                dest_fullpath_filename = os.path.join(dest_folder, f"{info['year']}{info['mon']}{info['day']}_{info['hr']}{info['min']}{info['sec']}_{info['model']}_{i}.{file_extention}" )
                while os.path.isfile(dest_fullpath_filename):
                    i = i + 1
                    dest_fullpath_filename = os.path.join(dest_folder, f"{info['year']}{info['mon']}{info['day']}_{info['hr']}{info['min']}{info['sec']}_{info['model']}_{i}.{file_extention}" )
                # Copy file over.
                if copy_file(src_fullpath_filename, dest_folder, dest_fullpath_filename, logger):
                    os.remove(src_fullpath_filename)
                    print(f'Copied {src_fullpath_filename} to {dest_fullpath_filename}')
        else:
            # Destination file does not exist.
            # Open the directory and look for a file of a similar name.
            # Note that some extensions can be upper or lower case, this function is used
            # to find files identical destination files just with extention where case does
            # not match. 
            if identical_file_already_exists(dest_folder, info['yyyymmdd_hhmmss'], src_fullpath_filename):
                print(f'DELETE {src_fullpath_filename}.')
                time.sleep(0.2)
                os.remove(src_fullpath_filename)
                # so we should be able to delete the source....
            else:
                if copy_file(src_fullpath_filename, dest_folder, dest_fullpath_filename, logger):
                    os.remove(src_fullpath_filename)
                    print(f'Copied {src_fullpath_filename} to {dest_fullpath_filename}')
    except Exception as e:
        print(f'EXIF data not found, using media info instead.')
        try:
            process_video(src_fullpath_filename, dest_folder)
            print(f'EXIF data not found, using media info instead.')
        except Exception as e2:
            print(f'Exception: {e2}')


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

def process_folder(src_folder: str, dst_folder: str, logger: MsgLogger) -> None:
    f_types = magic.Magic(mime=True)
    occurences: Dict[str, int] = {}

    try:
        for fullpath_filename in find_files(src_folder, ""):
            file_type = None
            file_info: Dict[str, str] = {}
            try:
                file_type = f_types.from_file(fullpath_filename)
                print(f"filename : {fullpath_filename}, {file_type}")
                if file_type == "image/jpeg": 
                    #process_image(fullpath_filename, dst_folder, "jpg")
                    file_info = jpeg_info(fullpath_filename, logger)
                    for key, value in file_info.items():
                        print(f'{key}, {value}')

                    if ok_tags(file_info, logger):
                        process_file(fullpath_filename, dst_folder, "jpg", file_info, logger)

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
