from unittest import TestCase
import unittest
import watson
import urllib
import json
import os
import atom
import session
import datetime
from urllib2 import urlopen, Request


class watsonTest(TestCase):

    def test_fast_strptime(self):
        test1="02/07/17 15:22"
        TIME_FORMAT = "%d/%m/%y %H:%M"
        result=atom.fastStrptime(test1,TIME_FORMAT)
        otherresult=datetime.datetime.strptime(test1,TIME_FORMAT)

        self.assertEqual(result,otherresult)


    def test_fast_strptime_from_watch(self):
        test1="01-Jan-2018 07:22"
        TIME_FORMAT = "%d-%b-%Y %H:%M"
        result=atom.fastStrptime(test1,TIME_FORMAT)
        otherresult=datetime.datetime.strptime(test1,TIME_FORMAT)

        self.assertEqual(result,otherresult)



    def test_get_sessions_works_with_no_atoms(self):
        atoms=[]
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),0)

    def test_read_heartrate_file(self):
        atoms=watson.heartrate_to_atoms("testinputs/heart.csv")
        self.assertEqual(len(atoms),164866)

    def test_count_awake_sessions(self):
        watson.args =lambda:None
        setattr(watson.args, 'action', 'sort')
        setattr(watson.args, 'd',None)
        setattr(watson.args, 'verbatim',None)
        TF = "%d-%b-%Y %H:%M"
        pre=watson.max_dist_between_logs
        watson.max_dist_between_logs=90
        atoms=watson.heartrate_to_atoms("testinputs/heartshort.csv")
        sessions=watson.get_sessions(atoms)
        watson.max_dist_between_logs=pre
        projects = list(set([entry.project for entry in sessions]))
       # for project in projects:
       #         watson.projectreport(project, sessions, True)

        self.assertEqual(len(sessions),140)

    def test_invert_sessions(self):
        pre=watson.max_dist_between_logs
        watson.max_dist_between_logs=90
        atoms=watson.heartrate_to_atoms("testinputs/heartshort.csv")
        sessions=watson.get_sessions(atoms)
        #print "XXX{}".format(sessions[0])
        sessions=watson.invert_sessions(sessions)
        watson.max_dist_between_logs=pre
        projects = list(set([entry.project for entry in sessions]))
     #   for project in projects:
     #           watson.projectreport(project, sessions, True)
        self.assertEqual(len(sessions),140)






if __name__=="__main__":
    unittest.main()
