import unittest
import sys
sys.path.append('../src')  #needed for command line execution
sys.path.append('src')  # needed for execution via Visual Studio Code

import image_video_time_utilities as iv_util

class TestImageVideoTimeUtilities(unittest.TestCase):

    def test_process_correct_number_of_arguments(self):

        # Given: the correct number of arguments in a list
        app_name = "one"
        arg1_name = "two"
        arg2_name = "three"
        
        arg_list = [app_name, arg1_name, arg2_name]

        # When: processing the argments
        flag, a2, a3 = iv_util.process_args(arg_list)
        
        # Then: the status flag is true, and the 2nd and 3rd
        # arguments are returned.
        self.assertEqual(True, flag)
        self.assertEqual(arg1_name, a2)
        self.assertEqual(arg2_name, a3)

    def test_process_too_few_arguments(self):

        # Given: only 1 argument in the list
        app_name = "one"
        
        arg_list = [app_name]

        # When: processing the argments
        flag, a2, a3 = iv_util.process_args(arg_list)
        
        # Then: the status flag is false, and no 2nd and 3rd
        # arguments are returned.
        self.assertEqual(False, flag)
        self.assertEqual("", a2)
        self.assertEqual("", a3)

    def test_process_too_many_arguments(self):

        # Given: too many arguments in the list
        app_name = "one"
        
        arg_list = [app_name, app_name, app_name, app_name]

        # When: processing the argments
        flag, a2, a3 = iv_util.process_args(arg_list)
        
        # Then: the status flag is false, and no 2nd and 3rd
        # arguments are returned.
        self.assertEqual(False, flag)
        self.assertEqual("", a2)
        self.assertEqual("", a3)


if __name__ == '__main__':
    unittest.main()