import unittest
import sys
sys.path.append('../src')  #needed for command line execution
sys.path.append('src')  # needed for execution via Visual Studio Code

import image_video_time_utilities as iv_util

class TestImageVideoTimeUtilities(unittest.TestCase):

    def test_process_args(self):
        app_name = "one"
        arg1_name = "two"
        arg2_name = "three"
        
        arg_list = [app_name, arg1_name, arg2_name]
        flag, a2, a3 = iv_util.process_args(arg_list)
        
        self.assertEqual(True, flag)
        self.assertEqual(arg1_name, a2)
        self.assertEqual(arg2_name, a3)


if __name__ == '__main__':
    unittest.main()