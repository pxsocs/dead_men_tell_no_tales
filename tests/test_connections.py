# How to run tests here:
# From the app parent directory:
# python3 -m tests.test_connections

# Add the main app directory so the modules can be imported
import sys
import os

testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

# Main Imports
from datetime import datetime
import unittest
import logging
from backend.comm import ntp_time


class TestCommunications(unittest.TestCase):

    def test_get_ntp_time(self):
        print('[i] Testing: NTP Time')
        tm = ntp_time()
        self.assertIsNotNone(tm)
        self.assertIsInstance(tm, datetime)
        print(f'✅ got NTP Time OK - result: {tm}')

    def test_send_email_message(self):
        print('[i] Testing: Send e-mail message')


if __name__ == '__main__':
    unittest.main()
