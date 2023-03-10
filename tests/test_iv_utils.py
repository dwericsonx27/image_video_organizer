import unittest
import pathlib
import os
import shutil
import sys
sys.path.append('../src')  #needed for command line execution
sys.path.append('src')  # needed for execution via Visual Studio Code
from msg_logger import MsgLogger, LogEntryType

import image_video_time_utilities as iv_util

def folder_name(full_path_file_name : str) -> str:
    folder_path = pathlib.Path(full_path_file_name)
    return str(folder_path.parent)

def recursive_remove(folder_name : str) -> None:
    shutil.rmtree(folder_name)

def create_file(file_name : str, content : str) -> bool:
    rtnval = False
    pathlib_parent = pathlib.Path(file_name)
    file_path = str(pathlib_parent.parent)
    if len(file_path) > 0:
        os.makedirs(file_path, exist_ok=True)
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

    def test_identical_file_already_exists_found_different_content(self):

        file_name_1 = "/tmp/t1/zzzzz.1"
        file_name_2 = "/tmp/t2/zzzzz.2"
        try:
            self.assertTrue(create_file(file_name_1, "Junk"))
            self.assertTrue(create_file(file_name_2, "Different Junk"))
            self.assertFalse(iv_util.identical_file_already_exists(folder_name(file_name_1), "zzzzz", file_name_2))
        except Exception as e:
            print(f'Exception was {e}')
        finally:
            recursive_remove(folder_name(file_name_1))
            recursive_remove(folder_name(file_name_2))

    def test_ok_tags_insufficient_data(self):
        info = dict()

        info['abc'] = "asdfafd"

        self.assertFalse(iv_util.ok_tags(info, MsgLogger()))

    def test_ok_tags(self):
        info = dict()

        info['model'] = "Nikon"
        info['year'] = "2023"
        info['mon'] = "01"
        info['day'] = "01"
        info['hr'] = "01"
        info['min'] = "01"
        info['sec'] = "01"
        info['hr_min_sec'] = "01_01_01"
        info['year_mon_day'] = "2023_01_01"
        info['file_time'] = "20230101_010101"
        info['file_name'] = "20230101_010101_Nikon"

        self.assertTrue(iv_util.ok_tags(info, MsgLogger()))

    def test_ok_tags_good_keys_bad_values(self):
        info = dict()
        logger = MsgLogger()

        info['model'] = "Nikon"
        info['year'] = "4000"
        info['mon'] = "01"
        info['day'] = "01"
        info['hr'] = "01"
        info['min'] = "01"
        info['sec'] = "01"
        info['year_mon_day'] = "2023_01_01"
        info['file_time'] = "20230101_010101"
        info['file_name'] = "20230101_010101_Nikon"
        self.assertFalse(iv_util.ok_tags(info, logger))

        info['year'] = "2023"
        info['mon'] = "23"
        self.assertFalse(iv_util.ok_tags(info, logger))

        info['mon'] = "00"
        self.assertFalse(iv_util.ok_tags(info, logger))

        info['mon'] = "01"
        info['day'] = "50"
        self.assertFalse(iv_util.ok_tags(info, logger))
        
        info['day'] = "00"
        self.assertFalse(iv_util.ok_tags(info, logger))
        
        info['day'] = "01"
        info['hr'] = "50"
        self.assertFalse(iv_util.ok_tags(info, logger))
        
        info['hr'] = "-1"
        self.assertFalse(iv_util.ok_tags(info, logger))
        
        info['hr'] = "01"
        info['min'] = "60"
        self.assertFalse(iv_util.ok_tags(info, logger))
        
        info['min'] = "-1"
        self.assertFalse(iv_util.ok_tags(info, logger))
        
        info['min'] = "01"
        info['sec'] = "60"
        self.assertFalse(iv_util.ok_tags(info, logger))
        
        info['sec'] = "-1"
        self.assertFalse(iv_util.ok_tags(info, logger))

    def test_process_folder(self):

        iv_util.process_folder("/tmp/tA", "/tmp/tB", MsgLogger())

if __name__ == '__main__':
    unittest.main()