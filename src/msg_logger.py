from enum import Enum
import datetime
 
class LogEntryType(Enum):
    Information = 1
    Warning = 2
    Error = 3

class MsgLogger:
    
    msg_cnt: int = 0
    
    def __init__(self) -> None:
        self.log = dict()
    
    def add_log(self, msg: str, msg_type: LogEntryType) -> None:
        self.log[self.msg_cnt] = dict()
        self.log[self.msg_cnt]['msg'] = msg
        self.log[self.msg_cnt]['type'] = msg_type
        time_zone = datetime.timezone.utc
        format = "%Y-%m-%dT%H:%M:%S%z"
        self.log[self.msg_cnt]['date'] = datetime.datetime.now(tz=time_zone).strftime(format)
        self.msg_cnt = self.msg_cnt + 1
        
    def output_log(self) -> None:
        i: int = 0
        while i < self.msg_cnt:
            print(self.log[i])
            i = i + 1
            
    def get_log_message(self, index: int) -> str:
        if index < 0 or index >= self.msg_cnt:
            raise Exception("Out of bounds index.")
        
        return self.log[index]['msg']
            
    def log_size(self) -> int:
        return self.msg_cnt