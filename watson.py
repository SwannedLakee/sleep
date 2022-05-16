#!/usr/bin/python
import math
import calendar_helper_functions as icalhelper
import datetime
from session import Session
from atom import Atom

__TIME_FORMAT = "%d/%m/%y %H:%M"
max_dist_between_logs = 15  # in minutes TODO these should be arguments for different types of input.
min_session_size = 15  # in minutes


def sleep_report(project_sessions):
        wake_list = [str(session.end)[11:] for session in project_sessions]
        length_list=[session.length() for session in project_sessions]
        #TODO make these pretty 
        print(("Mean Sleep Time: {}".format(avg_time(length_list))))

def avg_time(datetimes):
    total = sum(dt.total_seconds() for dt in datetimes)
    avg = total / len(datetimes)
    return datetime.timedelta(seconds=avg);


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

def make_sleep_file(atoms):
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

def invert_sessions(sessions):
    lastsession=sessions[0]
    new_sessions=[]
    for session in sessions:
        new_sessions.append(Session(session.project,lastsession.end,session.start,session.content))
        lastsession=session
    return new_sessions

def heartrate_to_atoms(filename):
    #01-May-2017 23:46,01-May-2017 23:46,69.0
    TF = "%d-%b-%Y %H:%M"
    timestamplength=len("01-May-2017 23:46")
    datelength=len("01-May-2017")
    content=icalhelper.get_content(filename)
    atoms=[]
    for a in content:
        start=a[datelength+1:timestamplength]
        date=a[:datelength]
        end=a[timestamplength+1+datelength+1:(timestamplength*2)+1]
        atoms.append(Atom(start,end,date,"Sleep","Alive",TF))#labeling it sleep is wrong, but it keep the same name for the inversion.
    atoms.pop(0)
    return atoms

def full_detect():
    watch_atoms=heartrate_to_atoms("/Volumes/Crucial X8/git/sleep/Heart Rate.csv")
    sleep_sessions=make_sleep_file(watch_atoms)
    for session in sleep_sessions:
        print(session)
    print("## All time")
    sleep_report(sleep_sessions)
    this_week = [i for i in sleep_sessions if days_old(i)<7]
    print("## Last 7 Days") 
    sleep_report(this_week)
