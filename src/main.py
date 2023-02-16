import sys
#import magic
#from typing import Dict

import image_video_time_utilities as iv_util

arg_status, src, dst = iv_util.process_args(sys.argv)

if ~arg_status:
    print ("Please provide source and destination directory")
    exit()

process_status = iv_util.process_folder(src, dst)

if ~process_status:
    print(f"Errors processing the folder: {src}")
