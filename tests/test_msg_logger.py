import unittest
import sys
sys.path.append('../src')  #needed for command line execution
sys.path.append('src')  # needed for execution via Visual Studio Code

from msg_logger import MsgLogger, LogEntryType
import msg_logger

class TestImageVideoTimeUtilities(unittest.TestCase):
    
    def test_empty_initial_log(self):
        logger = MsgLogger()
        
        self.assertEqual(0, logger.log_size())
        
    def test_add_one_message(self):
        logger = msg_logger.MsgLogger()
        logger.add_log("test message", LogEntryType.Information)
        
        self.assertEqual(1, logger.log_size())
        
    def test_added_msg_is_what_is_logged(self):
        logger = MsgLogger()
        msg = "test1"
        logger.add_log(msg, LogEntryType.Information)
        self.assertEqual(msg, logger.get_log_message(0))
        
    def test_exception_for_bad_index(self):
        logger = MsgLogger()
        msg = "test1"
        logger.add_log(msg, LogEntryType.Information)
        self.assertRaises(Exception ,logger.get_log_message, 1000)
        
        
        

if __name__ == '__main__':
    unittest.main()