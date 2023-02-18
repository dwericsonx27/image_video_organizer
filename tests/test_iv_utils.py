import unittest
import os
import sys
sys.path.append('../src')  #needed for command line execution
sys.path.append('src')  # needed for execution via Visual Studio Code

import image_video_time_utilities as iv_util

def create_file(file_name : str, content : str) -> bool:
    rtnval = False
    with open(file_name, "w") as fp:
        fp.write(f"{content}")
        rtnval = True
    return rtnval

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

    def test_identical_file_already_exists_missing(self):

        #iv_util.process_folder("/tmp/t1", "/tmp/t2")

        file_name = "/tmp/zzzzz.123"
        try:
            self.assertTrue(create_file(file_name, "Junk"))
            self.assertFalse(iv_util.identical_file_already_exists("/tmp/", "abc", file_name))
        finally:
            os.remove(file_name)

    def test_identical_file_already_exists_found_same_content(self):

        file_name_1 = "/tmp/zzzzz.1"
        file_name_2 = "/tmp/zzzzz.2"
        try:
            self.assertTrue(create_file(file_name_1, "Junk"))
            self.assertTrue(create_file(file_name_2, "Junk"))
            self.assertTrue(iv_util.identical_file_already_exists("/tmp/", "zzzzz", file_name_2))
        finally:
            os.remove(file_name_1)
            os.remove(file_name_2)

    @unittest.skip("Need to use different folders for this to work")
    def test_identical_file_already_exists_found_different_content(self):

        file_name_1 = "/tmp/zzzzz.1"
        file_name_2 = "/tmp/zzzzz.2"
        try:
            self.assertTrue(create_file(file_name_1, "Junk"))
            self.assertTrue(create_file(file_name_2, "Different Junk"))
            self.assertFalse(iv_util.identical_file_already_exists("/tmp/", "zzzzz", file_name_2))
        finally:
            os.remove(file_name_1)
            os.remove(file_name_2)


if __name__ == '__main__':
    unittest.main()