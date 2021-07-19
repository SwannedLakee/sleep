#!/usr/bin/python
import re
import sys
import math
import pytz
import calendar_helper_functions as icalhelper
import glob
import datetime
import argparse
import os
import json
import timechart
from session import Session
from atom import Atom


#Todo:
# (C) log file to atoms should take content rather than a filename

__TIME_FORMAT = "%d/%m/%y %H:%M"

max_dist_between_logs = 15  # in minutes TODO these should be arguments for different types of input.
min_session_size = 15  # in minutes

def setup_argument_list():
    "creates and parses the argument list for Watson"
    parser = argparse.ArgumentParser( description="manages Watson")
    parser.add_argument("action", help="What to do/display: options are 'sort', 'now', and 'sleep'")
    parser.add_argument('-d', nargs="?" , help="Show only tasks that are at least this many days old")
    parser.add_argument( '-v', dest='verbatim', action='store_true', help='Verbose mode')
    parser.set_defaults(verbatim=False)
    return parser.parse_args()


# Summary ######################################################################



def median(l):
# from https://stackoverflow.com/questions/24101524/finding-median-of-list-in-python
        l.sort()
        lent = len(l)
        if (lent%2)==0:
            m = int(lent/2)
            result = l[m]
        else:
            m = int(float(lent/2) -0.5)
            result = l[m]
        return ('median is: {}'.format(result))

def sleep_report(project_sessions):
        for entry in project_sessions:
            print entry
        total_time = sum([entry.length() for entry in project_sessions], datetime.timedelta())
        average_time = avg_time([entry.length() for entry in project_sessions])
        wake_list = [str(entry.end)[11:] for entry in project_sessions]
        st_dev_length = st_dev([entry.length() for entry in project_sessions])
        med = median([entry.length() for entry in project_sessions])
#TODO make these pretty 
        print "\nTotal Sleep Time: {}".format(str(total_time)[:-3])
        print "Medien Sleep Time: {}".format(str(med)) 
        print "Average Sleep Time: {}".format(str(average_time))
        print "Average Wake Time: {}".format(mean_time(wake_list))
        print "ST-dev for average: {}".format(str(st_dev_length))

        return total_time

from cmath import rect, phase
from math import radians, degrees

def mean_angle(deg):
    return degrees(phase(sum(rect(1, radians(d)) for d in deg)/len(deg)))

def mean_time(times):
    t = (time.split(':') for time in times)
    seconds = ((float(s) + int(m) * 60 + int(h) * 3600)
               for h, m, s in t)
    day = 24 * 60 * 60
    to_angles = [s * 360. / day for s in seconds]
    mean_as_angle = mean_angle(to_angles)
    mean_seconds = mean_as_angle * day / 360.
    if mean_seconds < 0:
        mean_seconds += day
    h, m = divmod(mean_seconds, 3600)
    m, s = divmod(m, 60)
    return '%02i:%02i:%02i' % (h, m, s)


def avg_time(datetimes):
    total = sum(dt.total_seconds() for dt in datetimes)
    avg = total / len(datetimes)
    return datetime.timedelta(seconds=avg);

def st_dev(datetimes):
    total = sum(dt.total_seconds() for dt in datetimes)
    avg = total / len(datetimes)
    #Now for standard devation
    #For each datapoint, find the square of it's difference from the mean and sum them.
    step1 = sum((dt.total_seconds()-avg)*(dt.total_seconds()-avg) for dt in datetimes)
    step2 = step1/len(datetimes)
    step3 = math.sqrt(step2)
    return datetime.timedelta(seconds=step3);


def days_old(session):
        delta = datetime.datetime.now() - session.start.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
	return delta.days

def get_sessions(atoms):
#This has two phases
        if len(atoms)==0:
            return []
        last= datetime.datetime.strptime( "11/07/10 10:00", __TIME_FORMAT)
        lasttitle=atoms[0].title
        current = atoms[0].get_S()
        grouped_timevalues=[]
        current_group=[]
    #Step1: group all atoms into the largest groups such that every start time but one is within 15 minutes of an end time of another
    #Oh- that's NOT*actually* what this does...this does 'within 15 minutes of the *last*'
        for current in atoms:
                if ((current.get_S()-last) > datetime.timedelta( minutes=max_dist_between_logs)):
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                elif (current.get_S() <last): #preventing negative times being approved...
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                elif (current.title != lasttitle): #preventing negative times being approved...
                    grouped_timevalues.append(current_group)
                    current_group=[current]
		last = current.get_E()
                lasttitle=current.title
                current_group.append(current)
        grouped_timevalues.append(current_group)
        #Step 2 - return those groups that are bigger than a set value.
        sessions=[]
        for i in grouped_timevalues:
            if i:
                if ((get_latest_end(i)-get_earliest_start(i)) >datetime.timedelta(minutes=min_session_size)):
                    sessions.append(Session(i[0].title,get_earliest_start(i),get_latest_end(i),i))
        return sessions


def get_latest_end(atoms):
    max=atoms[0].get_E()
    for atom in atoms:
        if atom.get_E()>max:
            max=atom.get_E()
    return max


def get_earliest_start(atoms):
    min=atoms[0].get_S()
    for atom in atoms:
        if atom.get_S()<min:
            min=atom.get_E()
    return min



def get_atom_clusters(atomsin):
    atoms=[]
    lastatom=atomsin[0]
    for atom in atomsin:
        if atom.start[:4]== lastatom.start[:4]:
            atom_minutes=int(atom.start[0:2])*60+int(atom.start[3:5])
            lastatom_minutes=int(lastatom.start[0:2])*60+int(lastatom.start[3:5])
            difference=atom_minutes-lastatom_minutes
            if difference<1:
                atom.title="Exercise"
                atoms.append(atom)
        lastatom=atom
    return atoms

def make_exercise_file(args,atoms):
     sessions=get_sessions(get_atom_clusters(atoms))
     timechart.graph_out(sessions,"exercise")
     return sessions

def make_sleep_file(args,atoms):
     global max_dist_between_logs
     global min_session_size
     pre=max_dist_between_logs
     pre2=min_session_size
     min_session_size = 60  # in minutes
     max_dist_between_logs=240

     sessions=get_sessions(atoms)
     sessions=invert_sessions(sessions)
     max_dist_between_logs=pre
     min_session_size = pre2
     return sessions

def make_projects_file(vision_dir, name):
    atoms=[]
    for file in glob.glob(vision_dir+"/*.md"):
        atoms.extend(log_file_to_atoms(file))
    sessions=get_sessions(atoms)
    timechart.graph_out(sessions,name)
    return sessions


def cut(atoms,start,end):
    TF = "%d-%b-%Y %H:%M"
    start_time= datetime.datetime.strptime( start, TF)
    end_time= datetime.datetime.strptime( end, TF)
    return_atoms=[]
    for current in atoms:
            if (current.get_S() > start_time):
                if (current.get_S() < end_time):
                    return_atoms.append(current)
    return return_atoms


def invert_sessions(sessions):
    lastsession=sessions[0]
    new_sessions=[]
    for session in sessions:
        new_sessions.append(Session(session.project,lastsession.end,session.start,session.content))
        lastsession=session
    return new_sessions


########## Input ##########



def heartrate_to_atoms(filename):
    #01-May-2017 23:46,01-May-2017 23:46,69.0
    TF = "%d-%b-%Y %H:%M"
    timestamplength=len("01-May-2017 23:46")
    datelength=len("01-May-2017")
    content=icalhelper.get_content(filename)
    if (args.d):
        if args.d:
            index=int(args.d)*1500
            content=content[len(content)-index:]
    atoms=[]
    for a in content:
        start=a[datelength+1:timestamplength]
        date=a[:datelength]
        end=a[timestamplength+1+datelength+1:(timestamplength*2)+1]
        atoms.append(Atom(start,end,date,"Sleep","Alive",TF))#labeling it sleep is wrong, but it keep the same name for the inversion.
    atoms.pop(0)
    return atoms







# Output

def calendar_output(filename,sessions, matchString=None):
        cal = icalhelper.get_cal()
        for entry in sessions:
            if (matchString==None) or (matchString==entry.project):
                icalhelper.add_event(cal, entry.project, entry.start, entry.end)
        icalhelper.write_cal(filename,cal)


def atoms_to_text(atoms):
    returntext=""
    lastdate=""

    for atom in atoms:
        if lastdate==atom.date:
            datestring=""
        else:
            datestring=" "+atom.date
            lastdate=atom.date
        if atom.start==atom.end:
            returntext+= "######"+datestring+ " "+ atom.start+","
        else:
            returntext+= "######"+datestring+ " "+ atom.start+ " to "+atom.end+","
        returntext+= "{}".format(atom.content)

    return returntext


def full_detect():
    watch_atoms=heartrate_to_atoms("/Users/joereddingtonfileless/git/Heart Rate.csv")
    sleep_sessions=make_sleep_file(args,watch_atoms)

    if args.d:
            sleep_sessions = [i for i in sleep_sessions if days_old(i)<int(args.d)]
    sleep_report(sleep_sessions)
    calendar_output(cwd+"/calendars/Sleep.ics",sleep_sessions)

