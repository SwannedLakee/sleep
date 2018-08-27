from unittest import TestCase
import unittest
import watson
import urllib
import json
import os
import atom
import session
from entry import Entry
import datetime
from urllib2 import urlopen, Request





class watsonTest(TestCase):


    def test_parse_line(self):
        entry=Entry("###### 27/08/18 00:01 to 07:53, +Sleep")
        self.assertEqual(entry.get_title(),"+Sleep")

    def test_parse_line_without_date(self):
        entry=Entry("###### 15:17, Making Watson great again.")
        self.assertEqual(entry.get_title(),"Making Watson great again.")


if __name__=="__main__":
    unittest.main()
