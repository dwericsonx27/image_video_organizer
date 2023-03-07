import unittest
import sys
sys.path.append('../src')  #needed for command line execution
sys.path.append('src')  # needed for execution via Visual Studio Code

import msg_logger

class TestImageVideoTimeUtilities(unittest.TestCase):
    
    def test_empty_initial_log(self):
        logger = msg_logger.MsgLogger()
        
        self.assertEqual(0, logger.log_size())
        
    def test_add_one_message(self):
        logger = msg_logger.MsgLogger()
        logger.add_log("test message")
        
        self.assertEqual(1, logger.log_size())
        
    def test_added_msg_is_what_is_logged(self):
        logger = msg_logger.MsgLogger()
        msg = "test1"
        logger.add_log(msg)
        self.assertEqual(msg, logger.get_log_message(0))
        
        

if __name__ == '__main__':
    unittest.main()