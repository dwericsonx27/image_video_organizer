import sys

import image_video_time_utilities as iv_util
from msg_logger import MsgLogger, LogEntryType

arg_status, src, dst = iv_util.process_args(sys.argv)

if ~arg_status:
    print ("Please provide source and destination directory")
    exit()

logger = MsgLogger()
process_status = iv_util.process_folder(src, dst, logger)

logger.output_log()

if ~process_status:
    print(f"Errors processing the folder: {src}")
