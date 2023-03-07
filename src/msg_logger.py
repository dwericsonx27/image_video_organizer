class MsgLogger:
    
    msg_cnt: int = 0
    
    def __init__(self) -> None:
    #def __init__(self):
        self.log = dict()
    
    def add_log(self, msg: str) -> None:
        self.log[self.msg_cnt] = msg
        self.msg_cnt = self.msg_cnt + 1
        
    def output_log(self) -> None:
        i: int = 0
        while i < self.msg_cnt:
            print(self.log[i])
            
    def get_log_message(self, index: int) -> str:
        if index < self.msg_cnt:
            return self.log[index]
        else:
            raise Exception("Out of bounds index.")
            
    def log_size(self) -> int:
        return self.msg_cnt