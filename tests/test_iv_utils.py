import unittest
import sys
sys.path.append('../src')

import image_video_time_utilities

class TestImageVideoTimeUtilities(unittest.TestCase):

    def test_process_args(self):
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()